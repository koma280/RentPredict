###############################################################################
# URL作成クラス
# Copyright 2021 tea-take, koma280. All rights reserved.
###############################################################################
import pandas as pd
import utility as utl

class urlgenerator:
    # クラス定数
    CB_STR = 'cb='
    CT_STR = 'ct='
    ET_STR = 'et='
    CN_STR = 'cn='
    MB_STR = 'mb='
    MT_STR = 'mt='
    MD_STR = 'md='
    EK_STR = 'ek='
    AP_STR = '&'

    # クラス変数
    BaseUrl = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ra=013'

    def __init__(self):
        # 路線情報を読み込む
        self.stationInfoDF = pd.read_csv("./list/StationInfoList.csv")
        # 駅徒歩を読み込む
        self.stationWalkingDictionary = utl.Csv_toDict_int("./list/StationWalkingList.csv")
        # 築年数を読み込む
        self.ageOfBuildingDictionary = utl.Csv_toDict_int("./list/AgeOfBuildingList.csv")
        # 専有面積下限を読み込む
        self.areaBottomDictionary = utl.Csv_toDict_int("./list/AreaBottomList.csv")
        # 専有面積上限を読み込む
        self.areaTopDictionary = utl.Csv_toDict_int("./list/AreaTopList.csv")
        # 賃料下限を読み込む
        self.costBottomDictionary = utl.Csv_toDict_float("./list/CostBottomList.csv")
        # 賃料上限を読み込む
        self.costTopDictionary = utl.Csv_toDict_float("./list/CostTopList.csv")
        # 間取りを読み込む
        self.floorPlanDictionary = utl.Csv_toDict_int("./list/FloorPlanList.csv")
        # インスタンス変数の初期化
        self.CostBottom = '0.0'
        self.CostTop = '9999999'
        self.StationWalking = '9999999'
        self.AgeOfBuilding = '9999999'
        self.AreaBottom = '9999999'
        self.AreaTop = '9999999'
        self.FloorPlan = []
        self.StationId = '0000000'

    def SetCost(self, bottom, top):
        self.CostBottom = str(bottom)
        self.CostTop = str(top)

    def SetStationWalking(self, value):
        self.StationWalking = str(value)

    def SetAgeOfBuilding(self, value):
        self.AgeOfBuilding = str(value)

    def SetArea(self, bottom, top):
        self.AreaBottom = str(bottom)
        self.AreaTop = str(top)

    def SetFloorPlan(self, values):
        if (type(values) is list):
            self.FloorPlan.clear()
            for value in values:
                self.FloorPlan.append(str(value).zfill(2))

    def SetStationInfo(self, lineName, stationName):
        self.StationId = str(list(self.stationInfoDF[self.stationInfoDF['路線名']==lineName][self.stationInfoDF['駅']==stationName]['駅ID'])).replace('[', '').replace(']', '').zfill(9)

    def Generate(self):
        result = self.BaseUrl + self.AP_STR
        # 賃料下限
        result += self.CB_STR + self.CostBottom + self.AP_STR
        # 賃料上限
        result += self.CT_STR + self.CostTop + self.AP_STR
        # 駅徒歩
        result += self.ET_STR + self.StationWalking + self.AP_STR
        # 築年数
        result += self.CN_STR + self.AgeOfBuilding + self.AP_STR
        # 間取り
        for fp in self.FloorPlan:
            result += self.MD_STR + fp + self.AP_STR
        # 専有面積下限
        result += self.MB_STR + self.AreaBottom + self.AP_STR
        # 専有面積上限
        result += self.MT_STR + self.AreaTop + self.AP_STR
        # 不明なもの
        result += 'shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&'
        # 駅ID
        result += self.EK_STR + self.StationId
        return result