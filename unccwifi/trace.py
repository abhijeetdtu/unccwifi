from unccwifi.student_count import StudentCount
from plotnine import *
import pathlib

class BuildingsPerStudent(StudentCount):

    def count(self , df):
        return df.groupby("username").apply(lambda df : df["building"].nunique()).reset_index().rename({0  : "nbuild"},axis=1)

    def plot(self,df):
        print(df.sort_values("nbuild" , ascending=False))
        p = (
            ggplot(df , aes(x="nbuild"))
            + geom_histogram()
            + ggtitle("Number of Buildings(unique) Visited by a user. \n Entire time period")
            + xlab("Number of Buildings")
            + ylab("Number of Users")
        )
        print(p)
        p.save(pathlib.Path(self.outputfolder , "temp.png") , "png")

    def pipe(self):
        df = self.read_all()
        count = self.count(df)
        self.save_to_csv(count.sort_values("nbuild" , ascending=False) , "build_per_student")
        self.plot(count)


if __name__ == "__main__":
    p = pathlib.Path("." , "output")
    BuildingsPerStudent(p,p).pipe()
