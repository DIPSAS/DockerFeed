from DockerFeed.Stores.AbstractStore import AbstractStore
from DockerFeed.VerificationHandler import VerificationHandler
from DockerFeed.Tools import StackTools, BatchProcessTools, SwarmInitTools
from DockerBuildSystem import DockerSwarmTools
import os
import warnings

class StackHandler:
    def __init__(self,
                 abstractStore: AbstractStore,
                 verificationHandler: VerificationHandler,
                 verifyStacksOnDeploy = False,
                 removeFilesFromCache = True,
                 swmInfrastructureFiles = [],
                 cacheFolder ='stacks',
                 logsFolder = 'logs',
                 noLogs = False,
                 ignoredStacks = []):

        self.__abstractStore = abstractStore
        self.__verificationHandler = verificationHandler
        self.__verifyStacksOnDeploy = verifyStacksOnDeploy
        self.__removeFilesFromCache = removeFilesFromCache
        self.__swmInfrastructureFiles = swmInfrastructureFiles
        self.__cacheFolder = cacheFolder
        self.__logsFolder = logsFolder
        self.__noLogs = noLogs
        self.__ignoredStacks = ignoredStacks


    def GetSource(self):
        return self.__abstractStore.GetSource()


    def Push(self, stackFiles: list):
        for stackFile in stackFiles:
            self.__abstractStore.Push(stackFile)
            print('Pushed {0} to source {1}'.format(stackFile, self.__abstractStore.GetSource()))


    def Pull(self, stacks = [], outputFolder = 'stacks'):
        stackFiles = self.__GetStackFilesFromStore(stacks)
        self.__PullStacks(stackFiles, outputFolder, showIgnoredStackWarning=True)
        print('Locate stacks in local storage: {0}'.format(self.__cacheFolder))


    def Init(self):
        SwarmInitTools.InitWithSwarmManager(self.__swmInfrastructureFiles)


    def Run(self, stacks = []):
        stackFiles = self.__GetStackFilesFromCache(stacks)
        sumExitCodes = 0
        for stackFile in stackFiles:
            exitCode = BatchProcessTools.ExecuteStackAsProcess(stackFile, self.__cacheFolder, self.__noLogs, self.__logsFolder)
            sumExitCodes += exitCode

        return sumExitCodes == 0


    def Deploy(self, stacks = []):
        stackFiles = self.__GetStackFilesFromCache(stacks)
        for stackFile in stackFiles:
            stackName = StackTools.ParseStackNameFromFilename(stackFile)

            valid = True
            if self.__verifyStacksOnDeploy:
                valid = self.__verificationHandler.VerifyStackFile(stackFile)

            if valid:
                DockerSwarmTools.DeployStack(stackFile, stackName)
            else:
                warnings.warn("Skipping deployment of stack {0} since it is invalid!".format(stackName))


    def Remove(self, stacks = []):
        stackFiles = self.__GetStackFilesFromCache(stacks)
        stackFilesToRemove = []
        for stackFile in stackFiles:
            stackName = StackTools.ParseStackNameFromFilename(stackFile)
            DockerSwarmTools.RemoveStack(stackName)
            stackFilesToRemove.append(stackFile)

        if self.__removeFilesFromCache:
            for removedStackFile in stackFilesToRemove:
                os.remove(removedStackFile)


    def Prune(self):
        self.Remove()
        SwarmInitTools.PruneWithSwarmManager(self.__swmInfrastructureFiles)


    def List(self, stackSearches = []):
        stackFiles = self.__GetStackFilesFromStore()
        return self.__FilterStackList(stackFiles, stackSearches)


    def Verify(self, stacks = []):
        stackFiles = self.__GetStackFilesFromCache(stacks)
        valid = True
        for stackFile in stackFiles:
            valid &= self.__verificationHandler.VerifyStackFile(stackFile)

        if valid:
            print("Successfully validated stacks!")
        else:
            warnings.warn("Stacks failed verification! See warnings in log.")

        return valid


    def __GetStackFilesFromCache(self, stacks = [], updateCacheFromStore = True):
        if updateCacheFromStore:
            stackFiles = self.__GetStackFilesFromStore(stacks)
            self.__PullStacks(stackFiles, self.__cacheFolder)
        stackFiles = StackTools.GetStackFilesFromCache(self.__cacheFolder, stacks)
        return StackTools.RemoveIgnoredStacksFromList(stackFiles, self.__ignoredStacks)


    def __GetStackFilesFromStore(self, stacks = []):
        stackFiles = self.__abstractStore.List()
        return StackTools.GetStackFileBaseNames(stackFiles, stacks)


    def __PullStacks(self, stackFiles: list, outputFolder: str, showIgnoredStackWarning = False):
        os.makedirs(outputFolder, exist_ok=True)
        for stackFile in stackFiles:
            stack = StackTools.ParseStackNameFromFilename(stackFile)
            if not(stack in self.__ignoredStacks):
                self.__abstractStore.Pull(stackFile, outputFolder)
            elif showIgnoredStackWarning:
                warnings.warn("Ignoring pull of stack {0}".format(stack))


    def __FilterStackList(self, stackFiles: list, stackSearches: list):
        stacks = []
        for stackFile in stackFiles:
            stackName = StackTools.ParseStackNameFromFilename(stackFile)
            if len(stackSearches) == 0:
                stacks.append(stackName)
            else:
                for stackSearch in stackSearches:
                    if stackSearch in stackName:
                        stacks.append(stackName)
                        break

        return stacks