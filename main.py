from bs4 import BeautifulSoup
import requests


def apply(url, selector, name='대', encode='utf-8', n=1, shift=0):
    resp = requests.get(url)

    if 'Div' in selector:
        # 유웨이는 euc-kr이고 div id에 Div가 들어감, 나머진 진학 어플라이
        resp.encoding = 'euc-kr'
    else:
        resp.encoding = encode

    html = resp.text

    bs = BeautifulSoup(html, 'html.parser')
    tags = bs.select('div#' + selector + " tr")
    body = tags[n].select('td')

    # shift가 있는 이유: 가끔 이유 모르게 하나씩 밀리는 경우가 있음 그러면 매개변수로 shift = 1 주면 됨
    return name + " " + body[0 + shift].text + ": " + body[2 + shift].text + "/" + body[1 + shift].text + " | " + body[3 + shift].text


res = apply('http://addon.jinhakapply.com/RatioV1/RatioH/Ratio10190201.html?1600824013879', selector='SelType436', name='가천대', n=2)
res += "\n" + apply('http://ratio.uwayapply.com/2021/susi2/kyonggi/1/', selector='Div_0076', name='경기대', n=15)
res += "\n" + apply('http://addon.jinhakapply.com/RatioV1/RatioH/Ratio11650301.html?1600905697121', selector='SelType4S', name='한양대에리카', n=1, shift=1)

print(res)
