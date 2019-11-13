import warnings
import os
import glob
from DockerFeed.Tools import StackVersionTools


def GetStackFilesInCache(cacheFolder: str, stacks = []):
    stackFiles = glob.glob(os.path.join(cacheFolder, 'docker-compose.*.y*ml'))
    resolvedStackFiles = StackVersionTools.GetResolvedStackFileVersions(stackFiles, stacks)
    return resolvedStackFiles


def GetStackDescriptionList(stackFiles: list, stackSearches: list, matchPartOfStackName: bool):
    resolvedStackFiles = StackVersionTools.GetResolvedStackFileVersions(stackFiles, stackSearches, matchPartOfStackName=matchPartOfStackName)
    stackDescriptions = []
    for resolvedStackFile in resolvedStackFiles:
        stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(resolvedStackFile)
        if not(stackFileIsValid):
            continue

        stackDescription = '{0}=={1}'.format(stackName, version)
        stackDescriptions.append(stackDescription)

    return stackDescriptions


def RemoveIgnoredStacksFromList(stackFiles: list, ignoredStacks: list):
    usedStackFiles = []
    for stackFile in stackFiles:
        stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile)
        if not(stackFileIsValid):
            continue

        if stackName in ignoredStacks:
            warnings.warn('Ignoring stack {0}.'.format(stackName))
        else:
            usedStackFiles.append(stackFile)

    return usedStackFiles
