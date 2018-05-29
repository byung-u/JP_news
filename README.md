# JP_news
JP news for korea realestate

Get Staff info 
---------------
* 스태프간 공유된 개인 정보는 xx/xx/xx/xx/xxx/xxx로 되어있다. 대략 아래와 같은 명령을 이용하면 골라 볼 수 있었다.
* 다만 url과 구분은 못한다는...

```
cat jp_staff.csv | cut -d ',' -f 3 | sed 's/"//g' | grep -E '((\/\w+)*\/)'
```
