from DockerFeed.Stores.AbstractStore import AbstractStore
from DockerFeed.VerificationHandler import VerificationHandler
from DockerFeed.Tools import StackTools, StackVersionTools, BatchProcessTools, SwarmInitTools
from DockerBuildSystem import DockerSwarmTools
import os
import warnings
import glob

class StackHandler:
    def __init__(self,
                 abstractStore: AbstractStore,
                 verificationHandler: VerificationHandler,
                 verifyStacksOnDeploy = False,
                 removeFilesFromCache = True,
                 swmInfrastructureFiles = [],
                 cacheFolder ='stacks',
                 logsFolder = 'logs',
                 outputFolder = 'stacks',
                 noLogs = False,
                 ignoredStacks = []):

        self.__abstractStore = abstractStore
        self.__verificationHandler = verificationHandler
        self.__verifyStacksOnDeploy = verifyStacksOnDeploy
        self.__removeFilesFromCache = removeFilesFromCache
        self.__swmInfrastructureFiles = swmInfrastructureFiles
        self.__cacheFolder = cacheFolder
        self.__logsFolder = logsFolder
        self.__outputFolder = outputFolder
        self.__noLogs = noLogs
        self.__ignoredStacks = ignoredStacks


    def GetSource(self):
        return self.__abstractStore.GetSource()


    def Push(self, stackFilePatterns: list):
        for stackFilePattern in stackFilePatterns:
            stackFiles = glob.glob(stackFilePattern)
            if len(stackFiles) == 0:
                warnings.warn("Could not detect any stack files to push with file pattern: {0}".format(stackFilePattern))
            for stackFile in stackFiles:
                self.__abstractStore.Push(stackFile)
                print('Pushed {0} to source {1}'.format(stackFile, self.__abstractStore.GetSource()))


    def Pull(self, stacks = []):
        stackFiles = self.__GetStackFilesFromStore(stacks)
        self.__PullStacks(stackFiles, self.__outputFolder, printInfo=True)


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
            stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile)
            if not(stackFileIsValid):
                continue

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
            stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile)
            if not(stackFileIsValid):
                continue

            DockerSwarmTools.RemoveStack(stackName)
            stackFilesToRemove.append(stackFile)

        if self.__removeFilesFromCache:
            for removedStackFile in stackFilesToRemove:
                os.remove(removedStackFile)


    def Prune(self):
        self.Remove()
        SwarmInitTools.PruneWithSwarmManager(self.__swmInfrastructureFiles)


    def List(self, stacks = []):
        stackFiles = self.__GetStackFilesFromStore(stacks)
        return StackTools.GetStackDescriptionList(stackFiles, stacks, matchPartOfStackName=False)


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
        stackFiles = StackTools.GetStackFilesInCache(self.__cacheFolder, stacks)
        return StackTools.RemoveIgnoredStacksFromList(stackFiles, self.__ignoredStacks)


    def __GetStackFilesFromStore(self, stacks = []):
        stackFiles = []

        for stack in stacks:
            spec = StackVersionTools.GetVersionSpecification(stack)
            searchPattern = 'docker-compose.{0}.*.y*ml'.format(spec.name)
            stackFiles += self.__abstractStore.List(searchPattern)

        if len(stacks) == 0:
            searchPattern = 'docker-compose.*.y*ml'.format()
            stackFiles += self.__abstractStore.List(searchPattern)

        stackFileArtifactNames = []
        for stackFile in stackFiles:
            stackFileArtifactName = os.path.basename(stackFile)
            if 'docker-compose.' in stackFileArtifactName:
                stackFileArtifactNames.append(stackFileArtifactName)
        return StackVersionTools.GetResolvedStackFileVersions(stackFileArtifactNames, stacks)


    def __PullStacks(self, stackFiles: list, outputFolder: str, printInfo = False):
        os.makedirs(outputFolder, exist_ok=True)
        for stackFile in stackFiles:
            stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile)
            if not(stackFileIsValid):
                continue

            if not(stackName in self.__ignoredStacks):
                self.__abstractStore.Pull(stackFile, outputFolder)
                if printInfo:
                    print("Pulled stack {0}=={1} to {2}".format(stackName, version, os.path.join(outputFolder, stackFile)))
            elif printInfo:
                warnings.warn("Ignoring pull of stack {0}".format(stackName))