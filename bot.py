import datetime

import aiohttp
import pyppeteer
from discord import Embed, Webhook, AsyncWebhookAdapter
from discord.ext import commands, tasks

from univ_ratio.dtutils import get_discord_timestamp
from univ_ratio.get_univ_ratio import UnivObject, UnivConfig


class UnivBot(commands.Bot):
    def __init__(self):
        super(UnivBot, self).__init__(command_prefix=['대학경쟁률 '], help_command=None)
        self.config: UnivConfig = UnivConfig.load()
        self.session = aiohttp.ClientSession()
        self.webhook = Webhook.from_url('YOUR_WEBHOOK_URL', adapter=AsyncWebhookAdapter(session=self.session))

        self.add_command(self.univ_ratio_cmd)
        self.add_command(self.ur_view_cmd)
        self.add_command(self.ur_update_cmd)

    async def on_ready(self):
        self.update_and_notify.start()

    async def close(self):
        self.config.save()
        self.update_and_notify.cancel()
        await self.session.close()
        await super(UnivBot, self).close()

    @tasks.loop(hours=1)
    async def update_and_notify(self):
        browser = await pyppeteer.launch(headless=True, args=[
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ])
        self.config.updated = datetime.datetime.utcnow().astimezone(tz=datetime.timezone.utc)
        for univ in self.config.univ_data.values():
            data = await univ.update(browser)
            if not univ.final:
                await self.webhook.send(
                    username=univ.name,
                    content=f'경쟁률이 갱신되었습니다!',
                    embed=Embed(
                        title=f'{univ.name} {data.name}',
                        description=f'갱신일자 : {get_discord_timestamp(self.config.updated)}'
                    ).add_field(
                        name='모집인원',
                        value=f'{data.recruit} 명',
                        inline=True
                    ).add_field(
                        name='지원자',
                        value=f'{data.apply} 명',
                        inline=True
                    ).add_field(
                        name='경쟁률',
                        value=f'{data.ratio} : 1',
                        inline=True
                    )
                )
        await browser.close()

    @commands.group(
        name='univ-ratio',
        aliases=['ur', '대학경쟁률', 'ㄷㄱ']
    )
    async def univ_ratio_cmd(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send(embed=Embed(
                title='별무리 - 대학경쟁률',
                description='대학 관련 기능입니다.'
            ).add_field(
                name='보기',
                value='대학경쟁률을 확인합니다.\n'
                      '`ㅂㅁㄹ 대학경쟁률 보기` 로 사용할 수 있습니다.',
                inline=False
            ).add_field(
                name='갱신',
                value='대학경쟁률을 수동으로 갱신합니다.\n'
                      '`ㅂㅁㄹ 대학경쟁률 갱신` 으로 사용할 수 있습니다.',
                inline=False
            ))

    @univ_ratio_cmd.command(
        name='view',
        aliases=['보기']
    )
    async def ur_view_cmd(self, ctx: commands.Context):
        embed = Embed(
            title='대학 경쟁률 정보',
            description='등록된 대학-전형의 경쟁률을 표시합니다.'
        )
        for univ in self.config.univ_data.values():
            embed.add_field(
                name=f'{univ.name} {univ.ratio_data.name}    ' if univ.ratio_data is not None else f'{univ.name} UNKNOWN    ' + '(최종)' if univ.final else '(갱신중)',
                value=f'{univ.ratio_data.ratio} : 1' if univ.ratio_data is not None else 'NOT PARSED',
                inline=False
            )
        await ctx.send(embed=embed)

    @univ_ratio_cmd.command(
        name='manual-update',
        aliases=['mu', '수동갱신', '갱신']
    )
    async def ur_update_cmd(self, ctx: commands.Context):
        await self.update_and_notify()
        await ctx.send('> 갱신했습니다.')


bot = UnivBot()
bot.run('YOUR_TOKEN')
