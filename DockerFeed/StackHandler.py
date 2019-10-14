from DockerFeed.ArtifactStore import ArtifactStore
from DockerFeed import InfrastructureHandler
from DockerFeed import VerificationHandler
from DockerBuildSystem import DockerSwarmTools, DockerComposeTools, TerminalTools, YamlTools, DockerImageTools
import os
import glob
import warnings
import random
from datetime import datetime

class StackHandler:
    def __init__(self,
                 artifactStore: ArtifactStore,
                 stacksFolder = 'stacks',
                 logsFolder = 'logs',
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
        self.__logsFolder = logsFolder
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


    def Run(self, stacks = None):
        sumExitCodes = 0
        if stacks is None:
            sumExitCodes += self.__RunStack()
        else:
            for stack in stacks:
                sumExitCodes += self.__RunStack(stack)

        return sumExitCodes == 0


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


    def __RunStack(self, stack = None):
        os.makedirs(self.__logsFolder, exist_ok=True)
        stackFileMatches = self.__GetStackFileMatches(stack)

        for environmentVariablesFile in self.__environmentFiles:
            TerminalTools.LoadEnvironmentVariables(environmentVariablesFile)

        sumExitCodes = 0
        for stackFile in stackFileMatches:
            stackName = self.__ParseStackNameFromComposeFilename(stackFile)
            if stackName in self.__ignoredStacks:
                warnings.warn("Ignoring execution of stack {0}".format(stackName))
                continue

            if not(stackName in self.__infrastructureStacks):
                temporaryStackFile = self.__GenerateStackFileWithContainerNames(stackFile)
                try:
                    DockerComposeTools.DockerComposeRemove([temporaryStackFile])
                    DockerComposeTools.DockerComposeUp([temporaryStackFile])
                    exitCode = self.__VerifyStackExecutedSuccessfully(temporaryStackFile, stackName)
                    DockerComposeTools.DockerComposeDown([temporaryStackFile])
                finally:
                    os.remove(temporaryStackFile)
                if exitCode > 0:
                    warnings.warn("Stack '" + stackName + "' FAILED!")
                else:
                    print(stackName + " stack finished with success.")
                sumExitCodes += exitCode

        return sumExitCodes


    def __GenerateStackFileWithContainerNames(self, stackFile: str):
        yamlData: dict = YamlTools.GetYamlData([stackFile])
        stackName = self.__ParseStackNameFromComposeFilename(stackFile)

        random.seed()
        randomId = random.randint(0, 1000)
        services = yamlData.get('services', [])
        for service in services:
            if not('container_name' in yamlData['services'][service]):
                yamlData['services'][service]['container_name'] = "{0}_{1}_{2}".format(stackName, service, randomId)

        temporaryStackFile = os.path.join(self.__stacksFolder, "docker-compose-temp.{0}.{1}.yml".format(stackName, randomId))
        YamlTools.DumpYamlDataToFile(yamlData, temporaryStackFile)
        return temporaryStackFile


    def __VerifyStackExecutedSuccessfully(self, temporaryStackFile: str, stackName: str):
        yamlData: dict = YamlTools.GetYamlData([temporaryStackFile])

        sumExitCodes = 0
        services = yamlData.get('services', [])
        for service in services:
            if not('container_name' in yamlData['services'][service]):
                raise Exception(("Cannot check exit code for service {0} in stack {1} " +
                              "due to missing container name tag.").format(service, stackName))

            containerName = yamlData['services'][service]['container_name']
            exitCode = DockerImageTools.GetContainerExitCode(containerName)
            self.__WriteLogsFromContainerToFile(containerName, service, stackName)
            sumExitCodes += exitCode
            if exitCode > 0:
                warnings.warn("Container '" + containerName + "' FAILED!")
            else:
                print(containerName + " container finished with success.")

        return sumExitCodes


    def __WriteLogsFromContainerToFile(self, containerName: str, service: str, stackName: str):
        logs = self.__GetLogsFromContainer(containerName)
        dateTimeNow = datetime.now()
        timestampStr = dateTimeNow.strftime("%Y%m%dT%H%M%S")
        logFile = os.path.join(self.__logsFolder, "{0}.{1}.{2}-{3}.log".format(stackName, service, containerName, timestampStr))
        with open(logFile, "a+") as f:
            f.write(logs)


    def __GetLogsFromContainer(self, containerName: str):
        terminalCommand = 'docker logs {0}'.format(containerName)
        logs = str(TerminalTools.ExecuteTerminalCommandAndGetOutput(terminalCommand).decode("utf-8"))
        return logs


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