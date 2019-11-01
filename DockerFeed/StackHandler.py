from DockerFeed.ArtifactStore import ArtifactStore
from DockerFeed import VerificationHandler
from DockerFeed import StackTools
from DockerBuildSystem import DockerSwarmTools, TerminalTools
import os
import glob
import warnings

class StackHandler:
    def __init__(self,
                 artifactStore: ArtifactStore,
                 swmInfrastructureFiles = [],
                 stacksFolder = 'stacks',
                 logsFolder = 'logs',
                 noLogs = False,
                 ignoredStacks = [],
                 offline = False,
                 removeFiles = False,
                 environmentFiles = [],
                 verifyImageDigest=True,
                 verifyImages=True,
                 verifyNoConfigs=True,
                 verifyNoSecrets=True,
                 verifyNoVolumes=True,
                 verifyNoPorts=True,
                 requiredImageLabels=VerificationHandler.DEFAULT_REQUIRED_IMAGE_LABELS):

        self.__artifactStore = artifactStore
        self.__swmInfrastructureFiles = swmInfrastructureFiles
        self.__stacksFolder = stacksFolder
        self.__logsFolder = logsFolder
        self.__noLogs = noLogs
        self.__ignoredStacks = ignoredStacks
        self.__offline = offline
        self.__removeFiles = removeFiles
        self.__environmentFiles = environmentFiles
        self.__verifyImageDigest = verifyImageDigest
        self.__verifyImages = verifyImages
        self.__verifyNoConfigs = verifyNoConfigs
        self.__verifyNoSecrets = verifyNoSecrets
        self.__verifyNoVolumes = verifyNoVolumes
        self.__verifyNoPorts = verifyNoPorts
        self.__requiredImageLabels = requiredImageLabels
        os.makedirs(self.__stacksFolder, exist_ok=True)

        if not(self.__offline):
            self.__artifactStore.RequestCredentials()


    def Push(self, composeFiles):
        for composeFile in composeFiles:
            self.__artifactStore.Push(composeFile)
            print('Pushed {0} to feed {1}'.format(composeFile, self.__artifactStore.GetFeedUri()))


    def Pull(self, stacks = None):
        if stacks is None:
            composeFiles = self.__GetStackNamesFromArtifactStore()
            for composeFile in composeFiles:
                stack = StackTools.ParseStackNameFromComposeFilename(composeFile)
                if stack in self.__ignoredStacks:
                    warnings.warn("Ignoring pull of stack {0}".format(stack))
                else:
                    self.__artifactStore.Pull(composeFile, self.__stacksFolder)
        else:
            for stack in stacks:
                if stack in self.__ignoredStacks:
                    warnings.warn("Ignoring pull of stack {0}".format(stack))
                else:
                    composeFile = 'docker-compose.{0}.yml'.format(stack)
                    self.__artifactStore.Pull(composeFile, self.__stacksFolder)
        print('Locate stacks in local storage: {0}'.format(self.__stacksFolder))


    def Init(self):
        StackTools.InitWithSwarmManager(self.__swmInfrastructureFiles)


    def Run(self, stacks = None):
        sumExitCodes = 0
        if stacks is None:
            sumExitCodes += self.__RunStack()
        else:
            for stack in stacks:
                sumExitCodes += self.__RunStack(stack)

        return sumExitCodes == 0


    def Deploy(self, stacks = None, verifyStacksOnDeploy=True):
        if stacks is None:
            self.__DeployStack(verifyStacksOnDeploy=verifyStacksOnDeploy)
        else:
            for stack in stacks:
                self.__DeployStack(stack, verifyStacksOnDeploy=verifyStacksOnDeploy)


    def Remove(self, stacks=None):
        if stacks is None:
            self.__RemoveStack()
        else:
            for stack in stacks:
                self.__RemoveStack(stack)


    def Prune(self):
        self.__RemoveStack()
        StackTools.PruneWithSwarmManager(self.__swmInfrastructureFiles)


    def List(self, stackSearches = None):
        stacks = []
        if self.__offline:
            stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.*.y*ml'))
        else:
            stackFileMatches = self.__GetStackNamesFromArtifactStore()

        for stackFileMatch in stackFileMatches:
            stackName = StackTools.ParseStackNameFromComposeFilename(stackFileMatch)
            if stackSearches is None:
                stacks.append(stackName)
            else:
                for stackSearch in stackSearches:
                    if stackSearch in stackName:
                        stacks.append(stackName)
                        break

        return stacks


    def Verify(self, stacks = None):
        if stacks is None:
            stackFileMatches = self.__GetStackFileMatches()
        else:
            stackFileMatches = []
            for stack in stacks:
                stackFileMatches += self.__GetStackFileMatches(stack)

        valid = True
        for stackFile in stackFileMatches:
            stackName = StackTools.ParseStackNameFromComposeFilename(stackFile)
            if stackName in self.__ignoredStacks:
                warnings.warn("Ignoring validation of stack {0}".format(stackName))
            else:
                valid &= self.__VerifyStack(stackFile)
        if valid:
            print("Successfully validated stacks!")
        else:
            warnings.warn("Stacks failed verification! See warnings in log.")

        return valid


    def __GetStackFileMatches(self, stack = None):
        if not(self.__offline):
            self.__PullStacks(stack)

        return StackTools.GetStackFileMatches(self.__stacksFolder, stack)


    def __GetStackNamesFromArtifactStore(self, stack = None):
        stacks = self.__artifactStore.List()
        return StackTools.GetStackNames(stacks, stack)


    def __PullStacks(self, stack = None):
        os.makedirs(self.__stacksFolder, exist_ok=True)
        composeStackBaseNames = self.__GetStackNamesFromArtifactStore(stack)
        for composeStackBaseName in composeStackBaseNames:
            self.__artifactStore.Pull(composeStackBaseName, self.__stacksFolder)


    def __RunStack(self, stack = None):
        stackFileMatches = self.__GetStackFileMatches(stack)

        for environmentVariablesFile in self.__environmentFiles:
            TerminalTools.LoadEnvironmentVariables(environmentVariablesFile)

        sumExitCodes = 0
        for stackFile in stackFileMatches:
            stackName = StackTools.ParseStackNameFromComposeFilename(stackFile)
            if stackName in self.__ignoredStacks:
                warnings.warn("Ignoring execution of stack {0}".format(stackName))
                continue

            exitCode = StackTools.ExecuteStackAsProcess(stackFile, self.__stacksFolder, self.__noLogs, self.__logsFolder)
            sumExitCodes += exitCode

        return sumExitCodes


    def __DeployStack(self, stack = None, verifyStacksOnDeploy=True):
        stackFileMatches = self.__GetStackFileMatches(stack)

        for stackFile in stackFileMatches:
            stackName = StackTools.ParseStackNameFromComposeFilename(stackFile)
            if stackName in self.__ignoredStacks:
                warnings.warn("Ignoring deployment of stack {0}".format(stackName))
                continue

            valid = True
            if verifyStacksOnDeploy:
                valid = self.__VerifyStack(stackFile)
            if valid:
                DockerSwarmTools.DeployStack(stackFile, stackName, self.__environmentFiles)
            else:
                warnings.warn("Skipping deployment of stack {0} since it is invalid!".format(stackName))


    def __RemoveStack(self, stack = None):
        removedStackFiles = []
        if stack is None:
            removedStackFiles += self.__RemoveAllStacks()
        elif stack in self.__ignoredStacks:
            warnings.warn("Ignoring removal of stack {0}".format(stack))
        else:
            DockerSwarmTools.RemoveStack(stack)
            stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.{0}.y*ml'.format(stack)))
            removedStackFiles += stackFileMatches

        if self.__removeFiles:
            for removedStackFile in removedStackFiles:
                os.remove(removedStackFile)


    def __RemoveAllStacks(self):
        removedStackFiles = []
        stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.*.y*ml'))
        for stackFile in stackFileMatches:
            stackName = StackTools.ParseStackNameFromComposeFilename(stackFile)
            if stackName in self.__ignoredStacks:
                warnings.warn("Ignoring removal of stack {0}".format(stackName))
            else:
                DockerSwarmTools.RemoveStack(stackName)
                removedStackFiles.append(stackFile)

        return removedStackFiles


    def __VerifyStack(self, stackFile):
        return VerificationHandler.VerifyComposeFile(stackFile,
                                                      self.__verifyImageDigest,
                                                      self.__verifyImages,
                                                      self.__verifyNoConfigs,
                                                      self.__verifyNoSecrets,
                                                      self.__verifyNoVolumes,
                                                      self.__verifyNoPorts,
                                                      self.__requiredImageLabels)