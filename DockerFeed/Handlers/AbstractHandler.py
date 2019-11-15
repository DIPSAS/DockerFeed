from DockerFeed.Stores.AbstractStore import AbstractStore
from DockerFeed.Tools import StackTools, SwarmInitTools
import abc

class AbstractHandler(abc.ABC):
    def __init__(self,
                 abstractStore: AbstractStore,
                 outputFolder: str,
                 ignored: list,
                 cacheFolder: str,
                 removeFilesFromCache: bool,
                 swmInfrastructureFiles: list,
                 artifactIdentifier: str):

        self._abstractStore = abstractStore
        self._outputFolder = outputFolder
        self._ignored = ignored
        self._cacheFolder = cacheFolder
        self._removeFilesFromCache = removeFilesFromCache
        self._swmInfrastructureFiles = swmInfrastructureFiles
        self._artifactIdentifier = artifactIdentifier

    @abc.abstractmethod
    def GetSource(self):
        return self._abstractStore.GetSource()


    @abc.abstractmethod
    def Push(self, filePatterns: list):
        StackTools.PushStacks(self._abstractStore, filePatterns)


    @abc.abstractmethod
    def Pull(self, artifacts=[]):
        stackFiles = self._GetFilesFromStore(artifacts)
        StackTools.PullStacks(self._abstractStore, stackFiles, self._ignored, self._outputFolder,
                              printInfo=True, artifactIdentifier=self._artifactIdentifier)

    @abc.abstractmethod
    def Init(self):
        SwarmInitTools.InitWithSwarmManager(self._swmInfrastructureFiles)

    @abc.abstractmethod
    def Run(self, artifacts=[]):
        pass

    @abc.abstractmethod
    def Deploy(self, artifacts=[]):
        pass

    @abc.abstractmethod
    def Remove(self, artifacts=[]):
        pass

    @abc.abstractmethod
    def Prune(self):
        SwarmInitTools.PruneWithSwarmManager(self._swmInfrastructureFiles)

    @abc.abstractmethod
    def List(self, artifacts=[]):
        stackFiles = self._GetFilesFromStore(artifacts)
        return StackTools.GetStackDescriptionList(stackFiles, artifacts, matchPartOfStackName=False,
                                                  artifactIdentifier=self._artifactIdentifier)

    @abc.abstractmethod
    def Verify(self, artifacts=[]):
        pass


    def _GetFilesFromCache(self, artifacts):
        return StackTools.GetStackFilesFromCache(self._abstractStore, self._cacheFolder, artifacts,
                                                 self._ignored,
                                                 updateCacheFromStore=True,
                                                 artifactIdentifier=self._artifactIdentifier)


    def _GetFilesFromStore(self, artifacts):
        return StackTools.GetStackFilesFromStore(self._abstractStore, artifacts, artifactIdentifier=self._artifactIdentifier)