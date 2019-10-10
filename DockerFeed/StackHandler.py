from DockerFeed.ArtifactStore import ArtifactStore
from DockerFeed import InfrastructureHandler
from DockerFeed import VerificationHandler
from DockerBuildSystem import DockerSwarmTools
import os
import glob
import warnings

class StackHandler:
    def __init__(self,
                 artifactStore: ArtifactStore,
                 stacksFolder = 'stacks',
                 infrastructureStacks = ['infrastructure'],
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
        self.__stacksFolder = stacksFolder
        self.__infrastructureStacks = infrastructureStacks
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
            composeFiles = self.__GetStackNames()
            for composeFile in composeFiles:
                stack = self.__ParseStackNameFromComposeFilename(composeFile)
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
        DockerSwarmTools.StartSwarm()
        for infrastructureStack in self.__infrastructureStacks:
            self.__DeployStack(infrastructureStack, ignoreInfrastructure=False)


    def Deploy(self, stacks = None, ignoreInfrastructure = True, verifyStacksOnDeploy=True):
        if stacks is None:
            self.__DeployStack(ignoreInfrastructure=ignoreInfrastructure, verifyStacksOnDeploy=verifyStacksOnDeploy)
        else:
            for stack in stacks:
                self.__DeployStack(stack, ignoreInfrastructure=ignoreInfrastructure, verifyStacksOnDeploy=verifyStacksOnDeploy)


    def Remove(self, stacks=None, ignoreInfrastructure=True):
        if stacks is None:
            self.__RemoveStack(ignoreInfrastructure=ignoreInfrastructure)
        else:
            for stack in stacks:
                self.__RemoveStack(stack, ignoreInfrastructure=ignoreInfrastructure)


    def Prune(self):
        self.__RemoveStack(ignoreInfrastructure=False)


    def List(self, stackSearches = None):
        stacks = []
        if self.__offline:
            stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.*.y*ml'))
        else:
            stackFileMatches = self.__GetStackNames()

        for stackFileMatch in stackFileMatches:
            stackName = self.__ParseStackNameFromComposeFilename(stackFileMatch)
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
            stackName = self.__ParseStackNameFromComposeFilename(stackFile)
            if stackName in self.__ignoredStacks:
                warnings.warn("Ignoring validation of stack {0}".format(stackName))
            elif not(stackName in self.__infrastructureStacks):
                valid &= self.__VerifyStack(stackFile)
        if valid:
            print("Successfully validated stacks!")
        else:
            warnings.warn("Stacks failed verification! See warnings in log.")

        return valid


    def __GetStackFileMatches(self, stack = None):
        if not(self.__offline):
            self.__PullStacks(stack)

        if stack is None:
            stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.*.y*ml'))
        else:
            stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.{0}.y*ml'.format(stack)))

        if len(stackFileMatches) == 0 and not (stack is None):
            warnings.warn('Could not find any stack files matching stack with name {0} in folder {1}!'.format(stack,
                                                                                                              self.__stacksFolder))
        elif len(stackFileMatches) == 0 and stack is None:
            warnings.warn('Could not find any stack files in folder {0}!'.format(self.__stacksFolder))

        return stackFileMatches


    def __GetStackNames(self, stack = None):
        stacks = self.__artifactStore.List()
        composeStackBaseNames = []
        for composeStackName in stacks:
            composeStackBaseName = os.path.basename(composeStackName)
            if 'docker-compose.' in composeStackBaseName:
                if stack is None or stack == self.__ParseStackNameFromComposeFilename(composeStackBaseName):
                    composeStackBaseNames.append(composeStackBaseName)

        return composeStackBaseNames


    def __PullStacks(self, stack = None):
        os.makedirs(self.__stacksFolder, exist_ok=True)
        composeStackBaseNames = self.__GetStackNames(stack)
        for composeStackBaseName in composeStackBaseNames:
            self.__artifactStore.Pull(composeStackBaseName, self.__stacksFolder)


    def __ParseStackNameFromComposeFilename(self, stackFile):
        stackFileBasename = os.path.basename(stackFile)
        stackName = stackFileBasename[stackFileBasename.find('docker-compose.') + 15:stackFileBasename.rfind('.')]
        return stackName


    def __DeployStack(self, stack = None, ignoreInfrastructure = True, verifyStacksOnDeploy=True):
        stackFileMatches = self.__GetStackFileMatches(stack)

        for stackFile in stackFileMatches:
            stackName = self.__ParseStackNameFromComposeFilename(stackFile)
            if stackName in self.__ignoredStacks:
                warnings.warn("Ignoring deployment of stack {0}".format(stackName))
                continue

            if stackName in self.__infrastructureStacks:
                if not(ignoreInfrastructure):
                    InfrastructureHandler.CreateInfrastructure(stackFile)
            else:
                valid = True
                if verifyStacksOnDeploy:
                    valid = self.__VerifyStack(stackFile)
                if valid:
                    DockerSwarmTools.DeployStack(stackFile, stackName, self.__environmentFiles)
                else:
                    warnings.warn("Skipping deployment of stack {0} since it is invalid!".format(stackName))


    def __RemoveStack(self, stack = None, ignoreInfrastructure = True):
        removedStackFiles = []
        if stack is None:
            removedStackFiles += self.__RemoveAllStacks(ignoreInfrastructure=ignoreInfrastructure)
        elif stack in self.__ignoredStacks:
            warnings.warn("Ignoring removal of stack {0}".format(stack))
        elif stack in self.__infrastructureStacks:
            if not(ignoreInfrastructure):
                stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.{0}.y*ml'.format(stack)))
                for stackFile in stackFileMatches:
                    InfrastructureHandler.RemoveInfrastructure(stackFile)
                    removedStackFiles.append(stackFile)
        else:
            DockerSwarmTools.RemoveStack(stack)
            stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.{0}.y*ml'.format(stack)))
            removedStackFiles += stackFileMatches

        if self.__removeFiles:
            for removedStackFile in removedStackFiles:
                os.remove(removedStackFile)


    def __RemoveAllStacks(self, ignoreInfrastructure):
        removedStackFiles = []
        infrastructureStackFiles = []
        stackFileMatches = glob.glob(os.path.join(self.__stacksFolder, 'docker-compose.*.y*ml'))
        for stackFile in stackFileMatches:
            stackName = self.__ParseStackNameFromComposeFilename(stackFile)
            if stackName in self.__ignoredStacks:
                warnings.warn("Ignoring removal of stack {0}".format(stackName))
            elif stackName in self.__infrastructureStacks:
                infrastructureStackFiles.append(stackFile)
            else:
                DockerSwarmTools.RemoveStack(stackName)
                removedStackFiles.append(stackFile)

        if not (ignoreInfrastructure):
            for infrastructureStackFile in infrastructureStackFiles:
                InfrastructureHandler.RemoveInfrastructure(infrastructureStackFile)
                removedStackFiles.append(infrastructureStackFile)

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