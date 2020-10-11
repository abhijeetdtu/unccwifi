tarpath= "test.tar"
expath = "tempdata"
import tarfile
tar = tarfile.open(tarpath)
tar.extractall(path=expath)
tar.close()

from unccwifi.process_file import ProcessFile
import pathlib

fname = tarpath.replace(".tar" , ".log")
processor = ProcessFile(pathlib.Path(expath ,fname).absolute() , pathlib.Path(".","output" ,fname).absolute())
processor.pipe()
