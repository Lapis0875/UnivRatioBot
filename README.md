# 대학 경쟁률 알리미
수시 원서 접수 기간중에, 경쟁률을 1시간마다 알림으로 받고 싶다는 생각을 하게 되었습니다. 
곧바로 디스코드 봇을 만들어, 원서 접수 기간동안 유용하게 사용했습니다 :D
앞으로 대학에 입학하실 후배님들의 합격을 기원하며, 이 봇은 오픈소스로 공개합니다.

## 사용법
`univ_ration` 경로에 경쟁률 크롤링 관련 코드들을 저장해두었습니다.
본래 디스코드 봇에서 사용할 것을 의도했으나, `univ_ration/get_univ_ratio.py` 에서 래핑해둔 객체들만 가지고 디스코드 봇이 아닌 다른 분야에도 응용 가능합니다.
크롤링은 `pyppeteer` 모듈을 사용해 진행합니다.

경쟁률 정보는 찾고자 하는 전형의 경쟁률 정보가 적힌 html 태그를 가져와 얻습니다.
`univ_ration/univ_ratio_config.json` 에 알림을 받고자 하는 대학 및 전형 정보를 기록합니다.
```json5
{
  "updated": null,    // 추후 동작하면서 데이터를 가져온 시점에 따라 갱신됩니다.
  "universities": {
    "한양대": {  // 대학 이름
      "ratio_url": "http://addon.jinhakapply.com/RatioV1/RatioH/Ratio11640141.html",            // 경쟁률 확인 페이지의 url      
      "target_xpath": "/html/body/form/div/div[2]/div[3]/div[1]/table/tbody/tr[3]",             // 한양대 학생부종합 경쟁률의 tr 태그의 full xpath.
      "type": "진학",   // 경쟁률 정보 페이지가 진학사이면 "진학", 유웨이이면 "유웨이" 로 기재합니다.
      "final": true    // 최종 경쟁률이면 true, 아니면 false. true 일경우 더이상 알림을 보내진 않지만, 명령어에서 확인 가능합니다.
    },
    "중앙대": {
      "ratio_url": "http://ratio.uwayapply.com/Sl5KOjhMSmYlJjomSmZmVGY",
      "target_xpath": "/html/body/div[2]/div/div[1]/div/div[2]/div[2]/table/tbody[1]/tr[4]",    // 중앙대 학생부종합
      "type": "유웨이",
      "final": false
    },
    "대학 이름": {
      // 대학 객체
    }
  }
}
```
### 대학 객체
```json5
{
  "ratio_url": "http://ratio.uwayapply.com/Sl5KOjhMSmYlJjomSmZmVGY",                        // 경쟁률 확인 페이지의 url   
  "target_xpath": "/html/body/div[2]/div/div[1]/div/div[2]/div[2]/table/tbody[1]/tr[4]",    // 알림을 받고자 하는 전형의 경쟁률 태그 (<tr>) 의 full xpath 입니다.
  "type": "유웨이",   // 경쟁률 정보 페이지가 진학사이면 "진학", 유웨이이면 "유웨이" 로 기재합니다.
  "final": true      // 최종 경쟁률이면 true, 아니면 false. true 일경우 더이상 알림을 보내진 않지만, 명령어에서 확인 가능합니다.
},
```