import pandas as pd
import os
import pathlib
from plotnine import *
import datetime


class StudentCount:

    def __init__(self,inputfolder , outputfolder):
        self.inputfolder = inputfolder
        self.outputfolder = outputfolder

    def read_all(self):
        dfs = []
        for f in os.listdir(self.inputfolder):
            if f.find("wireless") > -1 and f.find(".log") > -1:
                df = pd.read_csv(pathlib.Path(self.inputfolder , f))

                dfs.append(df)
        df =  pd.concat(dfs)
        df["time"] = pd.to_datetime(df["time"])
        return df

    def count(self,fdf):
         fdf["time"] = pd.to_datetime(fdf["time"])
         #fdf = fdf.set_index("time")
         dailyCounts = fdf.groupby(pd.Grouper(key="time" , freq="1d")).apply(lambda df: df["username"].nunique())

         return dailyCounts

    def save_to_csv(self,series , name=datetime.datetime.now().strftime("%m_%d")):
        if type(series) == pd.Series:
            series = series.to_frame()
        series.to_csv(pathlib.Path(self.outputfolder , name + ".csv").absolute())

    def pipe(self):
        fdf = self.read_all()
        series= self.count(fdf)
        self.save_to_csv(series)

if __name__ == "__main__":

    p = pathlib.Path("." , "output")

    class self:
        inputfolder = p
        outputfolder = p

    df = StudentCount(p , p).pipe()
    print(df)
