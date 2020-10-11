
f = open("tempdata/var/log/remote/wireless-encoded/wireless_10-01-2020.log")

data = []

i = 0
with open("tempdata/var/log/remote/wireless-encoded/wireless_10-06-2020.log") as f:
    for line in f:
        l = f.readline()
        mac = "64:51:06:66:77:c4"
        if l.find("Assoc success") > -1 and l.find("|AP") > -1:
            data.append(l.split(" "))
        #if l.find("Authentication Successful") > -1:
        #data.append(l.split(" "))

data[:20]

import numpy as np
import pandas as pd

df = pd.DataFrame(data)
cols = [3 , 10,17]

df
fdf = df.iloc[: , cols]
fdf = fdf.rename({3 : "time" , 10:"ap" , 17:"user"} , axis=1)
fdf["ap"] = fdf["ap"].apply(lambda r : r.split("@")[0])
fdf["building"] = fdf["ap"].apply(lambda r : r[0:4].lower() if r.find("EXT") < 0 else  r[4:8].lower() )
fdf["time"] = pd.to_datetime(fdf["time"] , format="%H:%M:%S")


fdf[fdf["user"] == "d0:d2:b0:92:df:70:"].groupby(pd.Grouper(key="time" , freq="15min")).size()


res =fdf.groupby([pd.Grouper(key="time" , freq="15min") , pd.Grouper(key="building")])["user"].nunique()


res = res.reset_index()
res["time"] = res["time"].apply(lambda t : (t.hour*60 + t.minute)/60)
from plotnine import *
(
ggplot(res , aes(x="time" , y="building" , fill="user"))
+ geom_tile()
+ theme(figure_size=(15,8))
)


(
ggplot( res.reset_index().groupby([pd.Grouper(key="time" , freq="15min")])["user"].sum().reset_index(), aes(x="time" , y="user"))
+ geom_line(group=1)
)
fdf["ap"]
res.reset_index().groupby([pd.Grouper(key="time" , freq="15min")])["user"].sum().reset_index()

res.reset_index().groupby([pd.Grouper(key="time" , freq="15min") , pd.Grouper(key="ap")])["user"].count()



res.reset_index().rename({0 : "count"} ,axis=1).pivot(columns="ap" , index=["time" , "user"] , values=["count"])

df.head()
df.shape
df.head()

if (df[1].unique() == [''])[0]:
    df = df.drop(1, axis=1)
    df.columns = np.arange(df.shape[1])

df
df.iloc[0]
df["time"] = df.iloc[:,:3].apply(lambda row : " ".join(row.values) , axis=1)
df["time"] = pd.to_datetime(df["time"] , format="%b %d %H:%M:%S")

df["time"] = df["time"].apply(lambda dt: dt.replace(year=2020))

df["time"]
df.iloc[0]
colsi= {14:"username", 15 : "mac" , 17 : "role" , 19 : "access_point" , 20:"ssid" }
df = df.rename(colsi,axis=1)
fdf = df[["time","username","mac","role" , "access_point" , "ssid"]]
fdf["building"] = fdf["access_point"].str.slice(3,7)

fdf
#fdf = fdf.set_index("time")
timeseries = (
    fdf.groupby([pd.Grouper(key='time', freq='15min')
                , pd.Grouper(key="building")])
                .apply(lambda df : len(df["mac"].unique()))
)

timeseries = timeseries.reset_index().rename({0:"n_unq"} , axis=1)
timeseries

#timeseries["building"] = timeseries["access_point"].str.slice(3,7)

timeseries["building"].unique()

from plotnine import *

(
ggplot(timeseries
, aes(x="time" , y="n_unq" , group="building" , color="building"))
+ geom_line()
+ facet_wrap("~ building")
+ scale_color_discrete(guide=False)
+ theme(figure_size=(10,7))
)
