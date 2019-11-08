import warnings
import os
import glob
import re
import semantic_version
import requirements


def GetStackNameFromStackFile(stackFile: str):
    stackName, version = GetStackNameAndVersionFromStackFile(stackFile)
    return stackName


def GetStackNameAndVersionFromStackFile(stackFile: str):
    stackFileBasename = os.path.basename(stackFile)
    stackName = stackFileBasename[stackFileBasename.find('docker-compose.') + 15:stackFileBasename.rfind('.')]
    matches = re.search('.[0-9]+', stackName).group()
    version = None
    if matches:
        versionStr = stackName[matches.span()[0]+1:]
        version = semantic_version.Version(versionStr)
        stackName = stackName[:matches.span()[0]]

    return (stackName, version)


def GetStackFilesInCache(cacheFolder: str, stacks = []):
    if len(stacks) == 0:
        stacks = GetAllStacksInCache(cacheFolder)

    stackFiles = []
    for stack in stacks:
        matchedStackFiles = glob.glob(os.path.join(cacheFolder, 'docker-compose.{0}.y*ml'.format(stack)))
        if len(matchedStackFiles) == 0:
            warnings.warn('Could not find any stack files matching stack with name {0} in cache folder {1}!'.format(stacks, cacheFolder))
        resolvedStackFiles = ResolveStacksFileWithVersion(matchedStackFiles, stack)
        stackFiles += resolvedStackFiles

    return stackFiles


def GetAllStacksInCache(cacheFolder: str):
    allStackFiles = glob.glob(os.path.join(cacheFolder, 'docker-compose.*.y*ml'))
    if len(allStackFiles) == 0:
        warnings.warn('Could not find any stack files in cache folder {0}!'.format(cacheFolder))
    stacks = []
    for stackFile in allStackFiles:
        stack = GetStackNameFromStackFile(stackFile)
        if not(stack in stacks):
            return stacks


def ResolveStacksFileWithVersion(stackFiles: list, stack: str):
    versionSpec = GetVersionSpecification(stack)
    resolvedStackFile = None
    newestVersion = None
    for stackFile in stackFiles:
        stackName, version = GetStackNameAndVersionFromStackFile(stackFile)
        if MatchVersionSpecification(versionSpec, version):
            if newestVersion is None or version > newestVersion:
                resolvedStackFile = stackFile
                newestVersion = version

    resolvedStackFiles = []
    if not(resolvedStackFile is None):
        resolvedStackFiles.append(resolvedStackFile)

    return resolvedStackFiles


def RemoveIgnoredStacksFromList(stackFiles: list, ignoredStacks: list):
    usedStackFiles = []
    for stackFile in stackFiles:
        stackFileBaseName = GetStackNameFromStackFile(stackFile)
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
            stackName = GetStackNameFromStackFile(stackFileBaseName)
            if len(stacks) == 0 or stackName in stacks:
                stackFileBaseNames.append(stackFileBaseName)

    return stackFileBaseNames


def GetVersionSpecification(stack: str):
    for req in requirements.parse(stack):
        return req.specs


def MatchVersionSpecification(versionSpec: list, version: semantic_version.Version):
    versionSpecStr = ''
    for versionTuple in versionSpec:
        if len(versionSpecStr) > 0:
            versionSpecStr += ','
        versionSpecStr += versionTuple[0] + versionTuple[1]

    if len(versionSpecStr) > 0:
        s = semantic_version.SimpleSpec(versionSpecStr)
        return s.match(version)
    else:
        return True
