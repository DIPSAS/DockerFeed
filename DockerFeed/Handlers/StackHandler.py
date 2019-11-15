from DockerFeed.Handlers.AbstractHandler import AbstractHandler
from DockerFeed.Stores.AbstractStore import AbstractStore
from DockerFeed.VerificationHandler import VerificationHandler
from DockerFeed.Tools import StackVersionTools, BatchProcessTools
from DockerBuildSystem import DockerSwarmTools
import os
import warnings

class StackHandler(AbstractHandler):
    def __init__(self,
                 abstractStore: AbstractStore,
                 verificationHandler: VerificationHandler,
                 verifyStacksOnDeploy = False,
                 removeFilesFromCache = True,
                 swmInfrastructureFiles = [],
                 cacheFolder ='cache',
                 logsFolder = 'logs',
                 outputFolder = 'stacks',
                 noLogs = False,
                 ignoredStacks = [],
                 artifactIdentifier = 'docker-compose.'):

        cacheFolder = os.path.join(cacheFolder, 'stacks')
        AbstractHandler.__init__(self, abstractStore,
                                 outputFolder,
                                 ignoredStacks,
                                 cacheFolder,
                                 removeFilesFromCache,
                                 swmInfrastructureFiles, artifactIdentifier)

        self.__verificationHandler = verificationHandler
        self.__verifyStacksOnDeploy = verifyStacksOnDeploy
        self.__logsFolder = logsFolder
        self.__noLogs = noLogs


    def GetSource(self):
        return super().GetSource()


    def Push(self, filePatterns: list):
        super().Push(filePatterns)


    def Pull(self, artifacts=[]):
        super().Pull(artifacts)


    def Init(self):
        super().Init()


    def Run(self, artifacts = []):
        stackFiles = self._GetFilesFromCache(artifacts)
        sumExitCodes = 0
        for stackFile in stackFiles:
            exitCode = BatchProcessTools.ExecuteStackAsProcess(stackFile, self._cacheFolder, self.__noLogs, self.__logsFolder,
                                                               artifactIdentifier=self._artifactIdentifier)
            sumExitCodes += exitCode

        return sumExitCodes == 0


    def Deploy(self, artifacts = []):
        stackFiles = self._GetFilesFromCache(artifacts)
        for stackFile in stackFiles:
            stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile,
                                                                                                         artifactIdentifier=self._artifactIdentifier)
            if not(stackFileIsValid):
                continue

            valid = True
            if self.__verifyStacksOnDeploy:
                valid = self.__verificationHandler.VerifyStackFile(stackFile)

            if valid:
                DockerSwarmTools.DeployStack(stackFile, stackName)
            else:
                warnings.warn("Skipping deployment of stack {0} since it is invalid!".format(stackName))


    def Remove(self, artifacts = []):
        stackFiles = self._GetFilesFromCache(artifacts)
        stackFilesToRemove = []
        for stackFile in stackFiles:
            stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile,
                                                                                                         artifactIdentifier=self._artifactIdentifier)
            if not(stackFileIsValid):
                continue

            DockerSwarmTools.RemoveStack(stackName)
            stackFilesToRemove.append(stackFile)

        if self._removeFilesFromCache:
            for removedStackFile in stackFilesToRemove:
                os.remove(removedStackFile)


    def Prune(self):
        self.Remove()
        super().Prune()


    def List(self, artifacts = []):
        return super().List(artifacts)


    def Verify(self, artifacts = []):
        stackFiles = self._GetFilesFromCache(artifacts)
        valid = True
        for stackFile in stackFiles:
            valid &= self.__verificationHandler.VerifyStackFile(stackFile)

        if valid:
            print("Successfully validated stacks!")
        else:
            warnings.warn("Stacks failed verification! See warnings in log.")

        return valid