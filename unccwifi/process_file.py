from plotnine import *
import pandas as pd
import numpy as np

class ProcessFile:

    def __init__(self,path , outpath):
        self.path = path
        self.outpath = outpath

    def read(self , path):

        data = []

        with open(self.path) as f:
            for line in f:
                l = f.readline()
                if l.find("Authentication Successful") > -1:
                    data.append(l.split(" "))

        return data

    def to_df(self,data):
        df = pd.DataFrame(data)

        if (df[1].unique() == [''])[0]:
            df = df.drop(1, axis=1)
            df.columns = np.arange(df.shape[1])

        df["time"] = df.iloc[:,:3].apply(lambda row : " ".join(row.values) , axis=1)
        df["time"] = pd.to_datetime(df["time"] , format="%b %d %H:%M:%S")

        df["time"] = df["time"].apply(lambda dt: dt.replace(year=2020))
        colsi= {14:"username", 15 : "mac" , 17 : "role" , 19 : "access_point" , 20:"ssid" }
        df = df.rename(colsi,axis=1)
        fdf = df[["time","username","mac","role" , "access_point" , "ssid"]]
        fdf["building"] = fdf["access_point"].str.slice(3,7)
        return fdf

    def df_to_csv(self,df):
        df.to_csv(self.outpath , index=False)

    def df_to_time_series(self,fdf):
        timeseries = (
            fdf.groupby([pd.Grouper(key='time', freq='15min')
                        , pd.Grouper(key="building")])
                        .apply(lambda df : len(df["mac"].unique()))
        )

    def timeseries_to_plot(self,timeseries):
        p = (
            ggplot(timeseries
            , aes(x="time" , y="n_unq" , group="building" , color="building"))
            + geom_line()
            + facet_wrap("~ building")
            + scale_color_discrete(guide=False)
            + theme(figure_size=(10,7))
        )
        print(p)

    def pipe(self):
        data = self.read(self.path)
        df = self.to_df(data)
        self.df_to_csv(df)

#fdf = fdf.set_index("time")

if __name__ == "__main__":
    processor = ProcessFile("wireless_09-14-2020/wireless_09-14-2020.log" , "output/09_14")
    processor.pipe()
