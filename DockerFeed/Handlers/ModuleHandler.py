from DockerFeed.Handlers.AbstractHandler import AbstractHandler
from DockerFeed.Stores.AbstractStore import AbstractStore
from DockerFeed.Handlers.StackHandler import StackHandler
from DockerFeed.Tools import ModuleTools
import os
import warnings

class ModuleHandler(AbstractHandler):
    def __init__(self,
                 abstractStore: AbstractStore,
                 stackHandler: StackHandler,
                 removeFilesFromCache = True,
                 swmInfrastructureFiles = [],
                 cacheFolder ='cache',
                 outputFolder = 'modules',
                 ignoredModules=[],
                 artifactIdentifier = 'docker-compose-module.'):

        cacheFolder = os.path.join(cacheFolder, 'modules')
        AbstractHandler.__init__(self, abstractStore,
                                 outputFolder,
                                 ignoredModules,
                                 cacheFolder,
                                 removeFilesFromCache,
                                 swmInfrastructureFiles, artifactIdentifier)

        self.__stackHandler = stackHandler


    def GetSource(self):
        return super().GetSource()


    def Push(self, filePatterns: list):
        super().Push(filePatterns)


    def Pull(self, artifacts=[]):
        super().Pull(artifacts)


    def Init(self):
        super().Init()


    def Run(self, artifacts = []):
        raise NotImplementedError("Run action is not implemented for handling modules, please do 'deploy' instead.")


    def Deploy(self, artifacts = []):
        moduleFiles = self._GetFilesFromCache(artifacts)
        for moduleFile in moduleFiles:
            ModuleTools.DeployModule(self.__stackHandler, moduleFile)


    def Remove(self, artifacts = []):
        moduleFiles = self._GetFilesFromCache(artifacts)
        moduleFilesToRemove = []
        for moduleFile in moduleFiles:
            ModuleTools.RemoveModule(self.__stackHandler, moduleFile)
            moduleFilesToRemove.append(moduleFile)

        if self._removeFilesFromCache:
            for moduleFileToRemove in moduleFilesToRemove:
                os.remove(moduleFileToRemove)


    def Prune(self):
        self.Remove()
        super().Prune()


    def List(self, artifacts = []):
        return super().List(artifacts)


    def Verify(self, artifacts = []):
        moduleFiles = self._GetFilesFromCache(artifacts)
        valid = True
        for moduleFile in moduleFiles:
            valid &= ModuleTools.VerifyModule(self.__stackHandler, moduleFile)

        if valid:
            print("Successfully validated modules!")
        else:
            warnings.warn("Modules failed verification! See warnings in log.")

        return valid