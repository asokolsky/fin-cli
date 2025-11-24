# {{longName}} | {{symbol}}:{{fullExchangeName}}

## Overview

{% if marketState == 'CLOSED' %}

|Current Price, Change (Change%)|Post Market Price, Change (Change%)|
|-------------------------------|-----------------------------------|
|{{currentPrice}} {{'%.2f' % regularMarketChange}} ({{'%.2f' % regularMarketChangePercent}}%)|{{'%.2f' % postMarketPrice}} {{'%.2f' % postMarketChange}} ({{'%.2f' % postMarketChangePercent}}%)|

{% else %}

|Current Price, Change (Change%)|
|-------------------------------|
|{{currentPrice}} {{'%.2f' % regularMarketChange}} ({{'%.2f' % regularMarketChangePercent}}%)|

{% endif %}


|.|.|.|.|
|-|-|-|-|
|Prev Close|{{'%.2f' % previousClose}}|Day's Range|{{regularMarketDayRange}}|
|Open|{{open}}|52 Week Range|{{fiftyTwoWeekRange}}|
|Bid|{{bid}}|Volume|{{format_num(volume)}}|
|Ask|{{ask}}|Avg Volume|{{format_num(averageVolume)}}|
|Market Cap|{{format_num(marketCap)}}|Earnings Date|{{earningsTimestamp}}|
|Beta|{{beta}}|Forward Dividend & Yield|???|
|PE (ttm)|{{trailingPE}}|Ex-Dividend Date|{{dividendDate}}|
|EPS (ttm)|{{'%.2f' % epsTrailingTwelveMonths}}|Target Price|{{targetMeanPrice}}|

## Business Summary

{{longBusinessSummary}}

{% if companyOfficers %}
## Corporate Officers
|Title|Name|Pay|Born|
|-----|----|---|----|
{% for officer in companyOfficers -%}
|{{ officer['title'] }}|{{ officer['name'] }}|{{ format_num(officer['totalPay']) }}|{{ officer['yearBorn'] }}|
{% endfor %}
{% endif %}

{% if corporateActions %}
## Corporate Actions
{% for action in corporateActions -%}
### {{action['header']}}
{{action['message']}}
{% endfor %}
{% endif %}
