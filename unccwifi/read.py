import numpy as np
import pandas as pd
import datetime
f = open("tempdata/var/log/remote/wireless-encoded/wireless_10-05-2020.log")


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
        mac = arr[4]
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

data = []

i = 0
with open("tempdata/var/log/remote/wireless-encoded/wireless_10-05-2020.log") as f:
    for line in f:
        le = None
        if (line.find("Deauth from") > -1):
            le = LogEntry(LogEntry.DEAUTH , line).get_entry_arr()
        if (line.find("Authentication Successful") > -1):
            le = LogEntry(LogEntry.AUTH , line).get_entry_arr()

        if le is not None:
            data.append(le)
            i += 1
        #if l.find("Authentication Successful") > -1:
        #    data.append(l.split(" "))
        #print(l)


#data

df = pd.DataFrame(data , columns=["type" , "time" , "ap" , "mac" , "user" , "ssid"])
#df.head()

df.shape
df["ap"].nunique()
24*60/15

def time_to_slot(time):
    return np.floor((time.hour*60 + time.minute)/ 15)

df["ap"].unique()

from collections import defaultdict

counter = defaultdict(lambda : defaultdict(set))
#counter = np.zeros(( int(24*60/15) , df["ap"].nunique() ))


df = df[df["time"] != '']
df["time"] =  pd.to_datetime(df["time"] , format="%b %d %H:%M:%S")

df["timeslot"] = df["time"].apply(lambda r : time_to_slot(r))

df.tail()
df.head()

def row_to_counter(row):
    slot = row["timeslot"]
    counterdf.loc[slot , row["ap"]] += -1 if row["type"] == LogEntry.DEAUTH else 1

def appointment(row):
    counterval = counter[row["timeslot"]][row["ap"]]
    if row["type"] == LogEntry.DEAUTH:
        if row["mac"] in counterval:
            counterval.remove(row["mac"])
    else:
        counterval.add(row["mac"])


df.apply(lambda row : appointment(row), axis=1)

#.apply(lambda df : df.apply(lambda row: row_to_counter(row), axis=1))

finaldata = []
for timeslot , access_point_dict in counter.items():
    for access_point , macs in access_point_dict.items():
        finaldata.append([timeslot , access_point , len(macs)])

finaldata

finaldf = pd.DataFrame(finaldata , columns=["timeslot" , "ap" , "count"])
finaldf["building"] = finaldf["ap"].apply(lambda r : r[0:4] if r.find("EXT") < 0 else  r[0:8] )
finaldf
#59*(15/(60))

finaldf.groupby(["timeslot" ,"building"])["count"].sum()
finaldf.sort_values("count" , ascending=False)
counterdf.sum(axis=1)


finaldf["time"] = finaldf["timeslot"]*15/60
from plotnine import *

(
    ggplot(finaldf.groupby("time")["count"].sum().reset_index() ,aes(x="time" , y="count"))
    + geom_line(group=1)
)
finaldf.groupby("timeslot")["count"].sum().reset_index()
