import warnings
import os
import glob
from DockerFeed.Tools import StackVersionTools


def GetStackFilesInCache(cacheFolder: str, stacks = []):
    stackFiles = glob.glob(os.path.join(cacheFolder, 'docker-compose.*.y*ml'))
    resolvedStackFiles = StackVersionTools.GetResolvedStackFileVersions(stackFiles, stacks)
    return resolvedStackFiles


def GetStackDescriptionList(stackFiles: list, stackSearches: list):
    resolvedStackFiles = StackVersionTools.GetResolvedStackFileVersions(stackFiles, stackSearches, matchPartOfStackName=True)
    stackDescriptions = []
    for resolvedStackFile in resolvedStackFiles:
        stackName, version = StackVersionTools.GetStackNameAndVersionFromStackFile(resolvedStackFile)
        stackDescription = '{0}=={1}'.format(stackName, version)
        stackDescriptions.append(stackDescription)

    return stackDescriptions


def RemoveIgnoredStacksFromList(stackFiles: list, ignoredStacks: list):
    usedStackFiles = []
    for stackFile in stackFiles:
        stackFileBaseName = StackVersionTools.GetStackNameFromStackFile(stackFile)
        if stackFileBaseName in ignoredStacks:
            warnings.warn('Ignoring stack {0}.'.format(stackFileBaseName))
        else:
            usedStackFiles.append(stackFile)

    return usedStackFiles
