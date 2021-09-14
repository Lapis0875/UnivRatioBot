import asyncio
import json
from datetime import datetime, timezone
from typing import Optional, NamedTuple

import pyppeteer.element_handle
from pyppeteer import launch
import dataclasses

from type_hints import JSON


REMOVE_UNNECESSARY_CHARS = str.maketrans('', '', '\t\n ')


@dataclasses.dataclass(init=True, repr=True, eq=True)
class UnivObject:
    name: str = dataclasses.field(repr=True, compare=False)
    type: str = dataclasses.field(repr=True, compare=False)
    ratio_url: str = dataclasses.field(repr=False, compare=False)
    target_xpath: str = dataclasses.field(repr=False, compare=False)
    final: bool = dataclasses.field(repr=True, default=False, compare=False)
    ratio_data: Optional['UnivRatioData'] = dataclasses.field(default=None, compare=True)

    @classmethod
    def from_json(cls, univ_name: str, data: JSON) -> 'UnivObject':
        return cls(
            name=univ_name,
            type=data['type'],
            ratio_url=data['ratio_url'],
            target_xpath=data['target_xpath'],
            final=data.get('final') or False
        )

    def to_json(self) -> JSON:
        return {
            'ratio_url': self.ratio_url,
            'target_xpath': self.target_xpath,
            'type': self.type,
            'final': self.final
        }

    async def update(self, browser) -> 'UnivRatioData':
        ratio = await get_apply_ratio(self, browser)
        # if self.ratio_data == ratio:
        #     self.final = True
        # else:
        #     self.ratio_data = ratio
        self.ratio_data = ratio
        return ratio


@dataclasses.dataclass(init=True, eq=False, repr=True)
class UnivConfig:
    updated: datetime = dataclasses.field(repr=True)
    univ_data: dict[str, UnivObject] = dataclasses.field(repr=False, default_factory=dict)

    @classmethod
    def from_json(cls, data: JSON) -> 'UnivConfig':
        return cls(
            updated=datetime.fromisoformat(data['updated']) if data['updated'] else datetime.utcnow().astimezone(tz=timezone.utc),
            univ_data=dict(map(
                lambda k_v: (k_v[0], UnivObject.from_json(*k_v)),
                data['universities'].items()
            ))
        )

    @classmethod
    def load(cls, path: str = './src/extensions/school/univ_ratio/univ_ratio_config.json'):
        with open(path, mode='rt', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_json(data)

    def to_json(self) -> JSON:
        return {
            'updated': self.updated.isoformat(),
            'universities': dict(map(
                lambda k_v: (k_v[0], k_v[1].to_json()),
                self.univ_data.items()
            ))
        }

    def save(self):
        with open('./univ_ratio/univ_ratio_config.json', mode='wt', encoding='utf-8') as f:
            json.dump(self.to_json(), fp=f, ensure_ascii=False, indent=2)


@dataclasses.dataclass(init=True, repr=True, eq=True, unsafe_hash=False, frozen=True)
class UnivRatioData:
    name: str = dataclasses.field(repr=True, compare=True)       # 모집전형
    recruit: int = dataclasses.field(repr=False, compare=True)    # 총모집인원
    apply: int = dataclasses.field(repr=False, compare=True)      # 지원인원
    ratio: float = dataclasses.field(repr=True, compare=True)    # 경쟁률


async def get_apply_ratio(univ: UnivObject, browser) -> Optional[UnivRatioData]:
    page = await browser.newPage()
    await page.goto(univ.ratio_url)
    # print(f'query for ratio data tag in univ {univ.name} ({univ.type})')
    ratio_tag: pyppeteer.element_handle.ElementHandle = await page.waitForXPath(univ.target_xpath, visible=True)
    # print(f'ratio_tag : {ratio_tag}')
    if not ratio_tag:
        return None

    if univ.type == '진학':
        # jinhakapply
        ratio_data_tags: list[pyppeteer.element_handle.ElementHandle] = await ratio_tag.querySelectorAllEval(
            'td',
            'nodes => nodes.map(n => n.innerText)'
        )
        # print(ratio_data_tags)
        name_tag, recruit_tag, apply_tag, ratio_tag = ratio_data_tags[:4]
        name = name_tag.translate(REMOVE_UNNECESSARY_CHARS)
        recruit = int(recruit_tag.replace(',', ''))
        appliers = int(apply_tag.replace(',', ''))
        ratio = float(ratio_tag.translate(REMOVE_UNNECESSARY_CHARS).split(':')[0])
        # print(f'모집인원 : {recruit}, 지원자 수 : {appliers}명, 경쟁률 : {ratio} : 1')
        return UnivRatioData(name, recruit, appliers, ratio)

    elif univ.type == '유웨이':
        # uwayapply
        ratio_data_tags: list[pyppeteer.element_handle.ElementHandle] = await ratio_tag.querySelectorAllEval(
            'td',
            'nodes => nodes.map(n => n.innerText)'
        )
        # print(ratio_data_tags)
        name_tag, recruit_tag, apply_tag, ratio_tag = ratio_data_tags[:4]
        name = name_tag.translate(REMOVE_UNNECESSARY_CHARS)
        recruit = int(recruit_tag.replace(',', ''))
        appliers = int(apply_tag.replace(',', ''))
        ratio = float(ratio_tag.translate(REMOVE_UNNECESSARY_CHARS).split(':')[0])
        # print(f'모집인원 : {recruit}, 지원자 수 : {appliers}명, 경쟁률 : {ratio} : 1')
        return UnivRatioData(name, recruit, appliers, ratio)


if __name__ == '__main__':
    # test code
    async def main():
        config = UnivConfig.load('./univ_ratio_config.json')
        for univ in config.univ_data.values():
            print(univ.name, ':', await univ.update())

    asyncio.run(main())
