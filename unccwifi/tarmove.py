# %load_ext autoreload
# %autoreload 2

import shutil
import os
import tarfile
from unccwifi.process_file import ProcessFile
from unccwifi.slot_track import SlotTrack
import pathlib
import time
import numpy as np
from multiprocessing import Pool
import argparse


class TarMove:

    def __init__(self,source_path , dest_path , startidx=0 , re=None , args=None):
        self.source_path = source_path
        self.dest_path = dest_path
        self.startidx = startidx
        self.re = re
        self.args = args

    def cleanDir(self,dir):
        filelist = [ f for f in os.listdir(dir) if f.endswith(".log") ]
        for f in filelist:
            os.remove(os.path.join(dir, f))

        shutil.rmtree(dir ,True)
        time.sleep(5)
        os.mkdir(dir)

    def _work(self , f):
        consider = True if self.re is None else f.find(self.re) > -1
        if (f.find(".tar.gz") > -1) and consider:
            print(f"Processing {f}")
            #tarpath= f.replace(".tar.gz" , ".log")
            tarpath = f.split(".")[0] + ".log"
            #shutil.copyfile(pathlib.Path(expath , f).absolute() , pathlib.Path(expath , f).absolute())
            print(f"-- Extraction Started")
            tar = tarfile.open(pathlib.Path(self.source_path , f).absolute())
            tar.extractall(path=self.dest_path)
            tar.close()
            print(f"-- Extraction done")

            if self.args.extractonly:
                return

            oname = tarpath.replace(".tar.gz" , ".csv")

            ndest_path = self.dest_path
            if f.find(".log") > -1:
                ndest_path = pathlib.Path(self.dest_path , "var" , "log" , "remote" , "wireless-encoded")
            #processor = ProcessFile(pathlib.Path(ndest_path ,tarpath).absolute() , pathlib.Path(".","output" ,oname).absolute())
            processor = SlotTrack(pathlib.Path(ndest_path ,tarpath).absolute() , pathlib.Path(".","output" ,oname).absolute())
            processor.pipe()
            print(f"-- Processing done")

    def Extract(self ):
        nsize = 4
        pool = Pool(nsize)
        re = self.re if self.re is not None else ".tar"
        allfiles = [f for f in  os.listdir(self.source_path) if (f.find(".tar.gz") > -1) and (f.find(re) > -1)]

        if self.args.endidx == -1:
            self.args.endidx = len(allfiles)
        if self.startidx < 0:
            self.startidx =  len(allfiles) + self.startidx #-1

        batches = [allfiles[(self.startidx + i*nsize ): min(self.startidx + (i+1)*nsize, self.args.endidx)] for i in range(int(len(allfiles)/nsize))]
        #print(batches)
        for batch in batches:
            if len(batch) == 0:
                continue
            print("-----------------Batch - " ,batch )
            pool.map(self._work , batch)

            if not self.args.extractonly:
               self.cleanDir(self.dest_path)


if __name__ == "__main__":
    source_path="F:\Data\BKP_Uncc_wifi"
    dest_path = pathlib.Path(".","tempdata").absolute()

    parser = argparse.ArgumentParser()
    parser.add_argument("--source" , default=source_path)
    parser.add_argument("--dest" , default=dest_path)
    parser.add_argument("--startidx" , default=0 , type=int)
    parser.add_argument("--endidx" , default=-1 , type=int)
    parser.add_argument("--re" , default=None)
    parser.add_argument("--extractonly" ,default=False , type=lambda t : t.lower()=="true")

    args = parser.parse_args()
    TarMove(args.source , args.dest , args.startidx , args.re , args).Extract()
