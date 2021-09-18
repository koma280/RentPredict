###############################################################################
# 予測関数
# Copyright 2021 tea-take, koma280. All rights reserved.
###############################################################################
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import pickle

def Prediction(dataframe, model_flg):
    # 予測用に項目を分ける
    # 家賃のみ
    if model_flg==False:
        x = dataframe[['築年数','物件階','面積','徒歩']]
        y = dataframe[['家賃']]

        # モデルをloadする
        loaded_model = pickle.load(open("./model/xgb_model.pickle", "rb"))

    # 家賃と管理費
    else:
        x = dataframe[['築年数','物件階','面積','徒歩']]
        y = dataframe[['家賃と管理費']]

        # モデルをloadする
        loaded_model = pickle.load(open("./model/xgb_model_add_manage.pickle", "rb"))

    try:
        # 集計した新しいDataFrameを作成する
        pd.options.display.float_format = '{:.1f}'.format
        df_pred = x
        df_pred['予測賃料'] = loaded_model.predict(x)
        df_pred['実賃料'] = y
        df_pred['差額'] = df_pred['実賃料'] - df_pred['予測賃料']
        df_pred['割引率（符号あり）'] = df_pred['差額'] / df_pred['実賃料']
        df_pred['割引率'] = df_pred['割引率（符号あり）'].abs()*100

        # 物件名とかを取ってくる
        df_joined = dataframe.join(df_pred,how = 'inner',rsuffix = '_right')

        # 並べ替えして欲しい項目だけ取ってくる
        df_hyoji = df_joined.sort_values('割引率（符号あり）')
        #df_hyoji['URL（表示用）'] = '<a href=' + df_hyoji['URL'] + '></a>' linkで飛べるようにしたかったが、あきらめる
        #df_hyoji = df_hyoji[['物件名','住所','路線','駅','徒歩','建物区分','築年数','物件階','間取り','面積','予測賃料','実賃料','割引率','URL']] URLありバージョン
        df_hyoji = df_hyoji[['物件名','住所','路線','駅','徒歩','建物区分','築年数','物件階','間取り','面積','予測賃料','実賃料','割引率']]


        return df_hyoji
    except:
        return None
