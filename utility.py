###############################################################################
# ユーティリティと言う名の何でも関数
# Copyright 2021 tea-take, koma280. All rights reserved.
###############################################################################
import csv
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd

##############################################################################
# CSVファイルをDictionaryとして読み込む
# (keysはfloat、valueは不定)
# file:CSVファイルへのパス
##############################################################################
def Csv_toDict_float(file):
    with open(file, newline="", encoding="utf-8") as f:
        read_dict = csv.DictReader(f, delimiter=",", quotechar='"')
        result = {}
        for row in read_dict:
            for k, v in row.items():
                temp = {float(k):v}
                result.update(temp)
    return result

##############################################################################
# CSVファイルをDictionaryとして読み込む
# (keysはint、valueは不定)
# file:CSVファイルへのパス
##############################################################################
def Csv_toDict_int(file):
    with open(file, newline="", encoding="utf-8") as f:
        read_dict = csv.DictReader(f, delimiter=",", quotechar='"')
        result = {}
        for row in read_dict:
            for k, v in row.items():
                temp = {int(k):v}
                result.update(temp)
    return result

##############################################################################
# スクレイピングの基準Urlから全ページUrlを取得
# baseUrl:Suumoの基準Url
##############################################################################
def CreateUrlList(baseUrl):
  # URLから情報を取得する
  result = requests.get(baseUrl)
  content = result.content
  soup = BeautifulSoup(content)

  # ページ情報、ページ数を取得する
  body = soup.find("body")
  pages = body.find_all("div", {'class':'pagination pagination_set-nav'})
  pages_text = str(pages)
  try:
    pages_split = pages_text.split('</a></li>\n</ol>')
    num_pages = int(pages_split[-1].split('>')[-1])
  except:
    try:
        pages_split = pages_text.split('</a></li>')
        num_pages = int(pages_split[-2].split('>')[-1])
    except:
        num_pages = 1

  # URLリストを作成する（お試しで2ページ分で実行）
  if num_pages >= 3:
      num_pages = 3

  urls = []
  urls.append(baseUrl)
  for i in range(1, num_pages):
    addUrl = baseUrl + "&page=" + str(i+1)
    urls.append(addUrl)

  return urls

##############################################################################
# スクレイピング
# urlList:urlのリスト
##############################################################################
def ScrapingSuumo(urlList):
  # 変数定義
  data = []
  name = ''
  build = ''
  address = ''
  station = []
  age = ''
  height = ''
  floor = ''
  rent = ''
  admin = ''
  shiki_deposit = ''
  rei_deposit = ''
  floor_plan = ''
  area = ''
  herf = ''
  URL = ''
  for url in urlList:
    # 4秒待つ！！これ重要！！
    time.sleep(3)

    # URLから情報を取得
    result = requests.get(url)
    content = result.content
    soup = BeautifulSoup(content)

    # ページ内の物件情報を取得
    summary = soup.find("div",{'id':'js-bukkenList'})

    try:
      m_prpty = summary.find_all("div",{'class':'cassetteitem'})
    except:
      return None

    for prp in m_prpty:
      # 物件名
      name = prp.find("div", {'class':'cassetteitem_content-title'}).string

      # 建物区分（アパート、マンション、戸建て）0503追加
      build = prp.find("span", {'class':'ui-pct ui-pct--util1'}).string

      # 住所
      address = prp.find("li", {'class':'cassetteitem_detail-col1'}).string

      # 最寄駅
      detail2 = prp.find("li", {'class':'cassetteitem_detail-col2'})
      stations = detail2.find_all("div", {'class':'cassetteitem_detail-text'})
      station.clear()
      for st in stations:
        station.append(st.string)

      # 築年数、階数
      detail3 = prp.find("li", {'class':'cassetteitem_detail-col3'})
      age = detail3.find_all("div")[0].string
      height = detail3.find_all("div")[1].string

      tbodies = prp.find_all("tbody")
      for tbody in tbodies:
        tds = tbody.find_all("td")
        for index, td in enumerate(tds):
          if (index == 2):
            # 部屋階数
            floor = td.string.strip()
          if (index == 3):
            # 賃料、管理費
            rent = td.find("span", {'class':'cassetteitem_other-emphasis ui-text--bold'}).string
            admin = td.find("span", {'class':'cassetteitem_price cassetteitem_price--administration'}).string
          if (index == 4):
            # 敷金、礼金
            shiki_deposit = td.find("span", {'class':'cassetteitem_price cassetteitem_price--deposit'}).string
            rei_deposit = td.find("span", {'class':'cassetteitem_price cassetteitem_price--gratuity'}).string
          if (index == 5):
            # 間取り、面積
            floor_plan = td.find("span", {'class','cassetteitem_madori'}).string
            area = td.find("span", {'class', 'cassetteitem_menseki'}).text
          if (index == 8):
            # URL 0503追加
            herf = str(td).split('"')[5]
            URL = 'https://suumo.jp' + herf

        # データを格納する
        data.append([name, station[0], station[1], station[2], build, address, age, height, floor, rent, admin, shiki_deposit, rei_deposit, floor_plan, area,URL])


  df = pd.DataFrame(data, columns=['物件名','立地1','立地2','立地3','建物区分','住所','築年数','階数','物件階','家賃','管理費','敷金','礼金','間取り','面積','URL'])
  return df

##############################################################################
# スクレイピングで取得したデータのクレンジング
# dataframe:スクレイピングで得たデータ
##############################################################################
def ModifyFormat(dataframe):
  dataframe['築年数'] = dataframe['築年数'].str.replace(u'新築',u'0')
  dataframe['築年数'] = dataframe['築年数'].str.replace(u'築',u'')
  dataframe['築年数'] = dataframe['築年数'].str.replace(u'年',u'')
  dataframe['築年数'] = dataframe['築年数'].str.replace(u'99以上',u'99')
  dataframe['築年数'] = pd.to_numeric(dataframe['築年数'])

  dataframe['階数'] = dataframe['階数'].str.replace(u'階建',u'')
  dataframe['階数'] = dataframe['階数'].str.replace(u'平屋',u'1')
  dataframe['階数'] = dataframe['階数'].apply(lambda x: x if len(x.strip('地下').split("地上")) < 2 else str(int(x.strip('地下').split("地上")[0]) + int(x.strip('地下').split("地上")[1])))
  dataframe['階数'] = pd.to_numeric(dataframe['階数'])

  dataframe['物件階'] = dataframe['物件階'].str.replace(u'階',u'')
  dataframe['物件階'] = dataframe['物件階'].str.replace(u'B',u'')
  dataframe['物件階'] = dataframe['物件階'].str.replace(u'M1',u'1')
  dataframe['物件階'] = dataframe['物件階'].str.replace(u'M2',u'2')
  dataframe['物件階'] = dataframe['物件階'].str.replace(u'M3',u'3')
  dataframe['物件階'] = dataframe['物件階'].str.replace(u'M4',u'4')
  dataframe['物件階'] = dataframe['物件階'].str.replace(u'M5',u'5')
  dataframe['物件階'] = dataframe['物件階'].apply(lambda x: x if len(x.split('-')) < 2 else (str(1) if x.split('-')[0] == '' else x.split('-')[0]))
  dataframe['物件階'] = pd.to_numeric(dataframe['物件階'])

  dataframe['家賃'] = dataframe['家賃'].str.replace(u'万円',u'')
  dataframe['家賃'] = pd.to_numeric(dataframe['家賃'])

  dataframe['管理費'] = dataframe['管理費'].str.replace(u'円',u'')
  dataframe['管理費'] = dataframe['管理費'].str.replace(u'-',u'0')
  dataframe['管理費'] = pd.to_numeric(dataframe['管理費'])

  dataframe['家賃と管理費'] = dataframe['家賃'] + (dataframe['管理費'] / 10000)

#  dataframe['敷金'] = dataframe['敷金'].str.replace(u'万円',u'')
#  dataframe['敷金'] = dataframe['敷金'].str.replace(u'-',u'0')
#  dataframe['敷金'] = pd.to_numeric(dataframe['敷金'])

#  dataframe['礼金'] = dataframe['礼金'].str.replace(u'万円',u'')
#  dataframe['礼金'] = dataframe['礼金'].str.replace(u'-',u'0')
#  dataframe['礼金'] = pd.to_numeric(dataframe['礼金'])

  dataframe['面積'] = dataframe['面積'].str.replace(u'm2',u'')
  dataframe['面積'] = pd.to_numeric(dataframe['面積'])

  dataframe['路線'] = [d[0] for d in dataframe['立地1'].str.split('/')]
  dataframe['駅徒歩'] = [d[1] for d in dataframe['立地1'].str.split('/')]
  dataframe['駅'] = [d[0] for d in dataframe['駅徒歩'].str.split(' ')]
  # 車やバスの考慮を行った。0503
  dataframe['徒歩'] = [d[1].replace(u'歩',u'').replace(u'分',u'').replace(u'バス',u'') for d in dataframe['駅徒歩'].str.split(' ')]
  dataframe['徒歩'] = dataframe['徒歩'].drop(dataframe[(dataframe['徒歩'].str.contains('車'))].index)
  dataframe['徒歩'] = pd.to_numeric(dataframe['徒歩'])

  # 欠損値削除
  dataframe = dataframe.dropna()

  # 列削除時に、dataframeを代入で更新したが、読み出し元で更新されなかったため戻り値に指定した
  return dataframe.drop(columns=['敷金', '礼金', '立地1', '立地2', '立地3', '駅徒歩', '階数'])
