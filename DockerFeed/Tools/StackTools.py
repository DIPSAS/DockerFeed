import warnings
import os
import glob
from DockerFeed.Tools import StackVersionTools
from DockerFeed.Stores.AbstractStore import AbstractStore


def GetStackFilesFromCache(abstractStore: AbstractStore,
                           cacheFolder: str,
                           stacks=[],
                           ignoredStacks=[],
                           updateCacheFromStore=True,
                           artifactIdentifier='docker-compose.'):

    if updateCacheFromStore:
        stackFiles = GetStackFilesFromStore(abstractStore, stacks, artifactIdentifier=artifactIdentifier)
        PullStacks(abstractStore, stackFiles, ignoredStacks, cacheFolder, artifactIdentifier=artifactIdentifier)
    stackFiles = GetStackFilesInCache(cacheFolder, stacks,
                                      artifactIdentifier=artifactIdentifier)
    return RemoveIgnoredStacksFromList(stackFiles, ignoredStacks,
                                       artifactIdentifier=artifactIdentifier)


def GetStackFilesFromStore(abstractStore: AbstractStore, stacks=[], artifactIdentifier='docker-compose.'):
    stackFiles = []

    for stack in stacks:
        spec = StackVersionTools.GetVersionSpecification(stack)
        searchPattern = '{0}{1}.*.y*ml'.format(artifactIdentifier, spec.name)
        stackFiles += abstractStore.List(searchPattern)

    if len(stacks) == 0:
        searchPattern = '{0}*.y*ml'.format(artifactIdentifier)
        stackFiles += abstractStore.List(searchPattern)

    stackFileArtifactNames = []
    for stackFile in stackFiles:
        stackFileArtifactName = os.path.basename(stackFile)
        if artifactIdentifier in stackFileArtifactName:
            stackFileArtifactNames.append(stackFileArtifactName)
    return StackVersionTools.GetResolvedStackFileVersions(stackFileArtifactNames, stacks,
                                                          artifactIdentifier=artifactIdentifier)

def PushStacks(abstractStore: AbstractStore, stackFilePatterns: list):
    for stackFilePattern in stackFilePatterns:
        stackFiles = glob.glob(stackFilePattern)
        if len(stackFiles) == 0:
            raise Exception("Could not detect any files to push with file pattern: {0}".format(stackFilePattern))
        for stackFile in stackFiles:
            abstractStore.Push(stackFile)
            print('Pushed {0} to source {1}'.format(stackFile, abstractStore.GetSource()))


def PullStacks(abstractStore: AbstractStore,
               stackFiles: list,
               ignoredStacks: list,
               outputFolder: str,
               printInfo=False,
               artifactIdentifier='docker-compose.'):

    os.makedirs(outputFolder, exist_ok=True)
    for stackFile in stackFiles:
        stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile,
                                                                                                     artifactIdentifier=artifactIdentifier)
        if not (stackFileIsValid):
            continue

        if not (stackName in ignoredStacks):
            abstractStore.Pull(stackFile, outputFolder)
            if printInfo:
                print("Pulled stack {0}=={1} to {2}".format(stackName, version, os.path.join(outputFolder, stackFile)))
        elif printInfo:
            warnings.warn("Ignoring pull of stack {0}".format(stackName))


def GetStackFilesInCache(cacheFolder: str, stacks=[], artifactIdentifier='docker-compose.'):
    stackFiles = glob.glob(os.path.join(cacheFolder, '{0}*.y*ml'.format(artifactIdentifier)))
    resolvedStackFiles = StackVersionTools.GetResolvedStackFileVersions(stackFiles, stacks,
                                                                        artifactIdentifier=artifactIdentifier)
    return resolvedStackFiles


def GetStackDescriptionList(stackFiles: list, stackSearches: list, matchPartOfStackName: bool, artifactIdentifier='docker-compose.'):
    resolvedStackFiles = StackVersionTools.GetResolvedStackFileVersions(stackFiles, stackSearches,
                                                                        artifactIdentifier=artifactIdentifier,
                                                                        matchPartOfStackName=matchPartOfStackName)
    stackDescriptions = []
    for resolvedStackFile in resolvedStackFiles:
        stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(resolvedStackFile,
                                                                                                     artifactIdentifier=artifactIdentifier)
        if not (stackFileIsValid):
            continue

        stackDescription = '{0}=={1}'.format(stackName, version)
        stackDescriptions.append(stackDescription)

    return stackDescriptions


def RemoveIgnoredStacksFromList(stackFiles: list, ignoredStacks: list, artifactIdentifier='docker-compose.'):
    usedStackFiles = []
    for stackFile in stackFiles:
        stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile,
                                                                                                     artifactIdentifier=artifactIdentifier)
        if not (stackFileIsValid):
            continue

        if stackName in ignoredStacks:
            warnings.warn('Ignoring stack {0}.'.format(stackName))
        else:
            usedStackFiles.append(stackFile)

    return usedStackFiles
