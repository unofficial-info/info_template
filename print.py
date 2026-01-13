import csv
from jinja2 import Template
from datetime import datetime
import locale

# 日本語曜日にする
locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")  # Mac/LinuxならOK、Windowsは別処理が必要

def format_date(date_str):
    """YYYY-MM-DD → YYYY/M/D(曜日) に変換"""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%Y/%-m/%-d(%a)")  # %-m, %-d はゼロ埋めなし (Mac/Linux)
    except:
        return date_str  # 変換失敗したらそのまま返す

def format_datetime(datetime_str):
    """YYYY-MM-DDTHH:MM:SS → M/D HH:MM に変換"""
    try:
        # T区切りの日時文字列をdatetimeオブジェクトに変換
        dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
        # ゼロ埋めなしの月日と時分にフォーマットして返す
        return dt.strftime("%-m/%-d(%a) %H:%M")
    except (ValueError, TypeError):
        # 変換に失敗した場合は元の文字列をそのまま返す
        return datetime_str
    
def format_google_cal(date_str, time_str):
    """
    date: 2026-01-27, time: 19:30 
    → 20260127T193000 に変換
    """
    if not date_str or not time_str:
        return ""
    # 記号（- と :）を取り除き、秒(00)を付与する
    clean_date = date_str.replace("-", "")
    clean_time = time_str.replace(":", "")
    return f"{clean_date}T{clean_time}00"

def format_google_cal_for_ticket(datetime_str):
    """YYYY-MM-DDTHH:MM:SS → YYYYMMDDTHHMMSS に変換"""

    cleandatetime = datetime_str.replace("-","").replace(":","")
    return f"{cleandatetime}"


# 新規ライブ情報のツイートテンプレ
newlive_template = """
🆕新規ライブ情報

『{{ title }}』

{{ date_formatted }}
⏰開場 {{ time_open }}｜開演 {{ time_start }}｜終演 {{ time_end }}
📍 {{ venue }}
🎫 {% if advance and door %}前売 ¥{{advance}}｜当日 ¥{{door}}{% elif advance %}前売 ¥{{advance}}{% elif door %}当日現金支払 ¥{{door}}{% endif %}
{% if preSaleStart %}
▼ {{ preSaleStart_formatted }}先行受付開始
{% elif general %}
▼ {{ general_formatted }}発売
{% else %}
▼ チケット販売中
{% endif %}{{ url }}
{% if streaming_url %}▼ 配信あり
{{ streaming_url }}{% endif %}
"""

# 明日のライブ情報のツイートテンプレ
nextlive_template = """
◤ {{date_formatted}}の予定 ◢

『{{ title }}』
🕰️ 開場 {{ time_open }}｜開演 {{ time_start }}{% if time_end %}｜終演 {{ time_end }} {% endif %}
📍 {{ venue }}
🎫 {% if advance and door %}前売 ¥{{advance}}｜当日 ¥{{door}}{% elif advance %}前売 ¥{{advance}}{% elif door %}当日現金支払 ¥{{door}}{% endif %} {{url}}
{% if streaming_url %}🎥 配信 ¥{{streaming_price}} {{streaming_url}}{% endif %}
"""

# lives.yml用のテンプレ
yml_template = """
- date: "{{ date }}"
  title: "{{ title }}"
  venue: "{{ venue }}"
  time_open: "{{ time_open }}"
  time_start: "{{ time_start }}"
  {% if time_end %}time_end: "{{ time_end }}"{% endif %}
  {% if preSaleStart %}preSale_start: "{{ preSaleStart }}"
  preSale_end: "{{ preSaleEnd }}"{% endif %}
  {% if general %}general: "{{ general }}"{% endif %}
  url: "{{ url }}"
  {% if streaming_url %}streaming_url: "{{ streaming_url }}"{% endif %}
"""

# フリカレ用のテンプレ
calender_template = """
{{ date }}
<div style="background-color:#cfe6da;"><font color="#696969">{{ title }}</div>
[詳細]
{{ time_start }}~{{ time_end }}(開場 {{ time_open }})
<b>『{{ title }}』</b>
📍 {{ venue }}
🎫 <a href="{{ url }}" target="_blank">{% if advance %}前売 ¥{{ advance }}{% elif door %}当日現金支払 ¥{{ door }}{% endif %}</a>{% if advance and door %}(¥{{ door }}){% endif %}
{% if streaming_url %}🎥 <a href="{{ streaming_url }}" target="_blank">{{streaming_price}}</a>{% endif %}
"""

# ニュース記事用のテンプレ
news_template ="""
---
layout: post
date: - - :00:00 + 0900
category: "LIVE"
title: "【 / 】{{ title }}【出演決定】"
---

<a href="https://www.google.com/calendar/render?action=TEMPLATE&text={{title}}&dates={{google_start}}/{{google_end}}&location={{venue}}" target="_blank" class="btn-calendar">
<i class="fa-solid fa-calendar-check"></i> Googleカレンダーに追加
</a>

# {{ title }}<br>

<i class="fa-regular fa-calendar-alt"></i> {{ date_formatted }}<br>
<i class="fa-regular fa-clock"></i> 開場 {{ time_open }} ｜開演 {{ time_start }} {% if time_end %}｜終演 {{ time_end }} {% endif %}<br>
<i class="fa-solid fa-location-dot"></i> {{ venue }}<br>
<i class="fa-solid fa-ticket"></i>  {% if advance and door %}前売 ¥{{advance}}｜当日 ¥{{door}}{% elif advance %}前売 ¥{{advance}}{% elif door %}当日現金支払 ¥{{door}}{% endif %}<br>
<i class="fa-solid fa-users"></i> {{ performer }}

{% if preSaleStart %}先行：{{ preSaleStart_formatted }} ~ {{ preSaleEnd_formatted }}
<a href="https://www.google.com/calendar/render?action=TEMPLATE&text=【先行】{{title}}&dates={{google_pre_start}}/{{google_pre_end}}&location={{url}}" target="_blank" class="btn-calendar">
<i class="fa-solid fa-calendar-check"></i>
</a><br>{% endif %}
{% if general %}一般：{{ general_formatted }}
<a href="https://www.google.com/calendar/render?action=TEMPLATE&text=【チケ発】{{title}}&dates={{google_general}}/{{google_general}}&location={{url}}" target="_blank" class="btn-calendar">
<i class="fa-solid fa-calendar-check"></i> 
</a>{% endif %}

チケットの購入は<a href="{{ url }}" target="_blank">こちら</a>
"""

mainlive_template ="""
- date: "{{ date }}"
  title: "{{ title }}"
  venue: "{{ venue }}"
  open: "{{ time_open }}"
  start: "{{ time_start }}"
  {% if time_end %}end: "{{ time_end }}"{% endif %}
  url: "{{ url }}"
"""

# CSV読み込み
with open("lives.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    lives = list(reader)

# 出力用バッファ
newlive_all = []
nextlive_all = []
yml_all = []
calender_all = []
news_all = []
mainlive_all = []

for live in lives:
    # 空欄対策
    live = {k: (v if v else "") for k, v in live.items()}

    # --- ここにカレンダー用の処理を追加 ---
    # 開始日時
    start_cal = format_google_cal(live["date"], live["time_start"])
    live["google_start"] = start_cal
    
    # 終了日時（空なら開始日時を入れる）
    if live["time_end"]:
        live["google_end"] = format_google_cal(live["date"], live["time_end"])
    else:
        live["google_end"] = start_cal

    if live["preSaleStart"]:
        live["google_pre_start"] = format_google_cal_for_ticket(live["preSaleStart"])
        live["google_pre_end"] =  format_google_cal_for_ticket(live["preSaleEnd"])

    if live["general"]:
        live["google_general"] = format_google_cal_for_ticket(live["general"])
    # ----------------------------------

    # 日付を整形
    live["date_formatted"] = format_date(live["date"])
    live["preSaleStart_formatted"] =  format_datetime(live["preSaleStart"])
    live["preSaleEnd_formatted"] = format_datetime(live["preSaleEnd"])
    live["general_formatted"] = format_datetime(live["general"])

    newlive_all.append(Template(newlive_template).render(live))
    nextlive_all.append(Template(nextlive_template).render(live))
    yml_all.append(Template(yml_template).render(live))
    calender_all.append(Template(calender_template).render(live))
    news_all.append(Template(news_template).render(live))
    mainlive_all.append(Template(mainlive_template).render(live))
    

# ファイル出力
with open("output/newlive.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(newlive_all))

with open("output/nextlive.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(nextlive_all))

with open("output/all_lives.yml", "w", encoding="utf-8") as f:
    f.write("\n".join(yml_all))

with open("output/calender.html", "w", encoding="utf-8") as f:
    f.write("\n".join(calender_all))

with open("output/news.html", "w", encoding="utf-8") as f:
    f.write("\n".join(news_all))

with open("output/mainlive.html", "w", encoding="utf-8") as f:
    f.write("\n".join(mainlive_all))

print("形式ごとに一覧ファイルを出力しました！")
