import os
import glob
import shutil
from DockerFeed.Stores.AbstractStore import AbstractStore

class FolderStore(AbstractStore):
    def __init__(self, \
                 sourceFolder ='stacks'):

        self.__sourceFolder = sourceFolder
        os.makedirs(self.__sourceFolder, exist_ok=True)


    def GetSource(self):
        return self.__sourceFolder


    def Pull(self, artifactName, outputFolder):
        sourcePath = self.__GetArtifactSourcePath(artifactName)
        destinationPath = os.path.join(outputFolder, artifactName)
        if not(os.path.isfile(sourcePath)):
            raise FileNotFoundError("Artifact {0} does not exist in source folder {1}".format(artifactName, self.__sourceFolder))

        os.makedirs(outputFolder, exist_ok=True)
        shutil.copyfile(sourcePath, destinationPath)


    def Push(self, artifactFile):
        destinationPath = os.path.join(self.__sourceFolder, os.path.basename(artifactFile))
        shutil.copyfile(artifactFile, destinationPath)


    def Exists(self, artifactName):
        sourcePath = self.__GetArtifactSourcePath(artifactName)
        return os.path.isfile(sourcePath)


    def Remove(self, artifactName):
        sourcePath = self.__GetArtifactSourcePath(artifactName)
        os.remove(sourcePath)


    def List(self):
        return glob.glob(os.path.join(self.__sourceFolder, '*'))


    def __GetArtifactSourcePath(self, artifactName):
        return os.path.join(self.__sourceFolder, artifactName)