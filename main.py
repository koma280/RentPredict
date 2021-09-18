###############################################################################
# メイン関数(streamlitで表示されるところ)
# Copyright 2021 tea-take, koma280. All rights reserved.
###############################################################################
import streamlit as st
import pandas as pd
import utility as utl
import urlgenerator
from pred import Prediction

# 路線情報を読み込む
stationInfoDF = pd.read_csv("./list/StationInfoList.csv")
lineNameList = stationInfoDF['路線名'].unique()

# 駅徒歩を読み込む
stationWalkingDictionary = utl.Csv_toDict_int("./list/StationWalkingList.csv")
stationWalkingList = list(stationWalkingDictionary.keys())

# 築年数を読み込む
ageOfBuildingDictionary = utl.Csv_toDict_int("./list/AgeOfBuildingList.csv")
ageOfBuildingList = list(ageOfBuildingDictionary.keys())

# 専有面積下限を読み込む
areaBottomDictionary = utl.Csv_toDict_int("./list/AreaBottomList.csv")
areaBottomList = list(areaBottomDictionary.keys())

# 専有面積上限を読み込む
areaTopDictionary = utl.Csv_toDict_int("./list/AreaTopList.csv")
areaTopList = list(areaTopDictionary.keys())

# 賃料下限を読み込む
costBottomDictionary = utl.Csv_toDict_float("./list/CostBottomList.csv")
costBottomList = list(costBottomDictionary.keys())

# 賃料上限を読み込む
costTopDictionary = utl.Csv_toDict_float("./list/CostTopList.csv")
costTopList = list(costTopDictionary.keys())

# 間取りを読み込む
floorPlanDictionary = utl.Csv_toDict_int("./list/FloorPlanList.csv")
floorPlanList = list(floorPlanDictionary.keys())

# URL Generatorインスタンス作成
urlgen = urlgenerator.urlgenerator()

##############################################################################
# メインバー
##############################################################################
st.title('物件検索')
st.header('使用目的')
st.write('使用時点の物件情報を検索し、割安物件を検索する')
st.header('使用方法')
st.write('左側のメニューバーから検索条件を設定し「予測」を実施する')
# st.header('予測対象URL')

##############################################################################
# 管理費込み選択コントロール定義
##############################################################################
include = st.sidebar.checkbox(
    '賃料に管理費を含める'
)

##############################################################################
# 路線名選択コントロール定義
##############################################################################
st.sidebar.write('路線')
lineName = st.sidebar.selectbox(
    '',
    lineNameList
)

##############################################################################
# 駅名選択コントロール定義
#   路線名選択コントロールにより選択項目の変化アリ
##############################################################################
st.sidebar.write('駅名')
# selectboxの第2引数は必ずList型であることdataframe型だとインタラクティブに動作しない！！
stationName = st.sidebar.selectbox(
    '',
    list(stationInfoDF[stationInfoDF['路線名']==lineName]['駅'])
)

# 駅情報を設定
urlgen.SetStationInfo(lineName, stationName)

##############################################################################
# 駅徒歩選択コントロール定義
##############################################################################
st.sidebar.write('駅徒歩')

# 駅徒歩のKey<->Valueの相互変換関数
def ConvertStationWalking(option):
    return stationWalkingDictionary[option]

stationWalking = st.sidebar.selectbox(
    '',
    stationWalkingList,
    format_func=ConvertStationWalking,
    index=6
)

# 駅徒歩を設定
urlgen.SetStationWalking(stationWalking)

##############################################################################
# 築年数選択コントロール定義
##############################################################################
st.sidebar.write('築年数')

# 築年数のKey<->Valueの相互変換関数
def ConvertAgeOfBuilding(option):
    return ageOfBuildingDictionary[option]

ageOfBuilding = st.sidebar.selectbox(
    '',
    ageOfBuildingList,
    format_func=ConvertAgeOfBuilding,
    index=10
)

# 築年数を設定
urlgen.SetAgeOfBuilding(ageOfBuilding)

##############################################################################
# 専有面積選択コントロール定義
##############################################################################
st.sidebar.write('専有面積')

# 専有面積下限のKey<->Valueの相互変換関数
def ConvertAreaBottom(option):
    return areaBottomDictionary[option]

cb = st.sidebar.selectbox(
    '',
    areaBottomList,
    format_func=ConvertAreaBottom,
    index=0
)

st.sidebar.write("～",)

# 専有面積上限のKey<->Valueの相互変換関数
def ConvertAreaTop(option):
    return areaTopDictionary[option]

ct = st.sidebar.selectbox(
    '',
    areaTopList,
    format_func=ConvertAreaTop,
    index=14
)

# 専有面積を設定
urlgen.SetArea(cb, ct)

##############################################################################
# 賃料選択コントロール定義
##############################################################################
st.sidebar.write('賃料')

# 賃料下限のKey<->Valueの相互変換関数
def ConvertCostBottom(option):
    return costBottomDictionary[option]

cb = st.sidebar.selectbox(
    '',
    costBottomList,
    format_func=ConvertCostBottom,
    index=5
)

st.sidebar.write("～",)

# 賃料上限のKey<->Valueの相互変換関数
def ConvertCostTop(option):
    return costTopDictionary[option]

ct = st.sidebar.selectbox(
    '',
    costTopList,
    format_func=ConvertCostTop,
    index=14
)

# 賃料の設定
urlgen.SetCost(cb, ct)

##############################################################################
# 間取り選択コントロール定義
##############################################################################
st.sidebar.write('間取り')

# 間取りのKey<->Valueの相互変換関数
def ConvertFloorPlan(option):
    return floorPlanDictionary[option]

mdlist = st.sidebar.multiselect(
    '',
    floorPlanList,
    format_func=ConvertFloorPlan
)

# 間取りの設定
urlgen.SetFloorPlan(mdlist)

# URL作成
urlResult = urlgen.Generate()
"""
[物件一覧](urlResult#streamlit.write)
urlResult
"""
# st.write(urlResult)

##############################################################################
# 実行コントロール定義
##############################################################################
buttonState = st.sidebar.button(
    '予測'
)
st.sidebar.write('予測には数秒かかります')

if buttonState:
    # 選択項目から読み込み対象のURLを取得
    urlList = utl.CreateUrlList(urlResult)

    # スクレイピング
    df = utl.ScrapingSuumo(urlList)
    if df is None:
        st.warning('物件がありません')
    else:
        # 前処理
        df = utl.ModifyFormat(df)

        # 予測
        df_disp = Prediction(df, include)
        

        ##############################################################################
        # 予測結果コントロール定義
        ##############################################################################
        if df_disp is None:
            st.warning('物件がありません')
        else:
            st.dataframe(df_disp)
