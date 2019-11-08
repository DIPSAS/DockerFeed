import warnings
import os
import glob
import semantic_version
import requirements


def ParseStackNameFromFilename(stackFile):
    stackFileBasename = os.path.basename(stackFile)
    stackName = stackFileBasename[stackFileBasename.find('docker-compose.') + 15:stackFileBasename.rfind('.')]
    return stackName


def GetStackFilesFromCache(cacheFolder: str, stacks = []):
    if len(stacks) == 0:
        stackFiles = glob.glob(os.path.join(cacheFolder, 'docker-compose.*.y*ml'))
        if len(stackFiles) == 0:
            warnings.warn('Could not find any stack files in cache folder {0}!'.format(cacheFolder))
    else:
        stackFiles = []
        for stack in stacks:
            matchedStackFiles = glob.glob(os.path.join(cacheFolder, 'docker-compose.{0}.y*ml'.format(stack)))
            if len(matchedStackFiles) == 0:
                warnings.warn('Could not find any stack files matching stack with name {0} in cache folder {1}!'.format(stacks, cacheFolder))
            stackFiles += matchedStackFiles

    return stackFiles


def RemoveIgnoredStacksFromList(stackFiles: list, ignoredStacks: list):
    usedStackFiles = []
    for stackFile in stackFiles:
        stackFileBaseName = ParseStackNameFromFilename(stackFile)
        if stackFileBaseName in ignoredStacks:
            warnings.warn('Ignoring stack {0}.'.format(stackFileBaseName))
        else:
            usedStackFiles.append(stackFile)

    return usedStackFiles


def GetStackFileBaseNames(stackFiles: list, stacks = []):
    stackFileBaseNames = []
    for stackFile in stackFiles:
        stackFileBaseName = os.path.basename(stackFile)
        if 'docker-compose.' in stackFileBaseName:
            stackName = ParseStackNameFromFilename(stackFileBaseName)
            if len(stacks) == 0 or stackName in stacks:
                stackFileBaseNames.append(stackFileBaseName)

    return stackFileBaseNames


def GetVersionSpecification(stack: str):
    for req in requirements.parse(stack):
        return req.specs


def ResolveStackFileWithVersion(cacheFolder: str, stack: str):
    matchedStackFiles = glob.glob(os.path.join(cacheFolder, 'docker-compose.{0}.y*ml'.format(stack)))

    versionSpec = GetVersionSpecification(stack)
    version = semantic_version.Version('0.1.1+build')
    for matchedStackFile in matchedStackFiles
        if len(versionSpec) == 0:
            
        else:


