import numpy as np
import pandas as pd
import datetime
from collections import defaultdict



class LogEntry:

    DEAUTH = 1
    AUTH = 2

    class EntryDetails:
        def __init__(self,type ,time,ap , mac,user='',ssid=''):
            self.type = type
            self.time = time
            self.ap = ap
            self.mac = mac
            self.user = user
            self.ssid = ssid

        def to_array(self):
            return [self.type , self.time , self.ap , self.mac , self.user , self.ssid]

    def __init__(self,type,line):
        self.type = type
        self.line = line
        self.keepi = {
            LogEntry.DEAUTH : [0,2,3,10 , 16],
            LogEntry.AUTH : [0,2,3,15,16,20,21]
        }

    def get_entry(self):
        if self.type == LogEntry.DEAUTH:
            return self._get_deauth_entry()
        else:
            return self._get_auth_entry()

    def get_entry_arr(self):
        return self.get_entry().to_array()

    def _get_deauth_entry(self):
        arr = np.array(self.line.split(" "))[self.keepi[LogEntry.DEAUTH]]
        time = " ".join(arr[0:3])
        ap = arr[3].split("@")[0]
        mac = arr[4].strip(": ")
        return LogEntry.EntryDetails(LogEntry.DEAUTH,time,ap,mac , "" , "")

    def _get_auth_entry(self):
        #print(self.line)
        try:
            arr = np.array(self.line.split(" "))[self.keepi[LogEntry.AUTH]]
            time = " ".join(arr[0:3])
            ap = arr[5].split("=")[1]
            mac = arr[4].split("=")[1]
            user = arr[3].split("=")[1]
            ssid = arr[6]
        except:
            arr,time,ap,mac,user,ssid ='','','','','',''
        return LogEntry.EntryDetails(LogEntry.AUTH,time , ap,mac,user,ssid)


class UserTrack:

    class UserInfo:

        def __init__(self,event,ap):
            self.last_event = event
            self.ap = ap

    def __init__(self):
        self.info = defaultdict(UserTrack.UserInfo)

class SlotTrack:

    def __init__(self, source_path , dest_path):
        self.source_path = source_path
        self.dest_path = dest_path
        self.user_track = UserTrack()

    def time_to_slot(self,time):
        return np.floor((time.hour*60 + time.minute)/ 15)

    def get_access_building_df(self):
        access_to_build = pd.read_excel("access_points_bldgs_merged.xlsx")
        access_to_build["Device"] = access_to_build["Device"].str.lower()
        return access_to_build

    def read_data(self):

        data = []

        with open(self.source_path) as f:
            for line in f:
                l = f.readline()
                if l.find("Assoc success") > -1 and l.find("|AP") > -1:
                    data.append(l.split(" "))

            return data

    def to_df(self,data):
        access_build = self.get_access_building_df()
        df = pd.DataFrame(data)

        if df.iloc[0,1] != '':
            cols = [0,1,2,9,16]
        else:
            cols = [0,2,3, 10,17]

        fdf = df.iloc[: , cols]

        #print(df.iloc[0, :])
        #print(df)

        renames = {key:val for val,key in zip(["month" , "day" , "time" , "ap" , "mac"],cols)}
        fdf = fdf.rename(renames , axis=1)
        fdf["ap"] = fdf["ap"].apply(lambda r : r.split("@")[0].lower())
        fdf["building"] = fdf["ap"].apply(lambda r : r[0:4].lower() if r.find("EXT") < 0 else  r[4:8].lower() )
        fdf['time'] = fdf["month"] + "-" + fdf["day"] + "-" +fdf["time"]
        fdf["time"] = pd.to_datetime(fdf["time"] , format="%b-%d-%H:%M:%S")
        fdf["time"] = fdf["time"].apply(lambda t : t.replace(year=2020))
        fdf["mac"] = fdf["mac"].apply(lambda r : r.strip(": "))
        fdf = fdf = pd.merge(fdf, access_build , left_on="ap" , right_on="Device" , how="left")[["month" , "day","time" , "ap" , "mac" ,"Matched_Building"]]
        fdf = fdf.rename({"Matched_Building" : "building"} , axis=1)
        fdf = fdf[~fdf["building"].isna()]
        #fdf[fdf["user"] == "d0:d2:b0:92:df:70:"].groupby(pd.Grouper(key="time" , freq="15min")).size()
        return fdf

    def discrete_buildings(self,fdf):

        def figure_out_building(df):
            vcs = df["building"].value_counts()
            if vcs[vcs.index[0]] ==0:
                return "-"
            else:
                return vcs.index[0]
        user_time_series= fdf.groupby( [pd.Grouper(key="mac"),pd.Grouper(key="time" , freq="15min")]).apply(lambda df : figure_out_building(df))
        user_time_series = user_time_series.reset_index().rename({0 : "building"} , axis=1)
        return user_time_series

    def final_building_counts(self, user_time_series):
        final_building_counts = user_time_series.groupby([pd.Grouper(key="time" , freq="15min") , pd.Grouper("building")]).apply(lambda df : df["mac"].nunique())
        final_building_counts = final_building_counts.reset_index().rename({0 : "n_unq_mac"}, axis=1)
        final_building_counts = final_building_counts[final_building_counts["building"] !="-"]
        return final_building_counts

    def save_to_csv(self , df):
        df.to_csv(self.dest_path)

    def pipe(self):
        data = self.read_data()
        fdf = self.to_df(data)

        user_time_series = self.discrete_buildings(fdf)
        self.save_to_csv(user_time_series)


if __name__ == "__main__":
    SlotTrack("tempdata/var/log/remote/wireless-encoded/wireless_10-05-2020.log"
    ,"output/wireless_10-05-2020.log").pipe()
