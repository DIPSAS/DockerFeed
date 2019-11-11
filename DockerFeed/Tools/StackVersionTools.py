import os
import re
import semantic_version
import requirements


def GetResolvedStackFileVersions(stackFiles: list, stacks: list, matchPartOfStackName = False):
    if len(stacks) == 0:
        stacks = GetStackNamesFromStackFiles(stackFiles)

    resolvedStackFiles = []
    for stack in stacks:
        resolvedStackFile = GetResolvedStackFileVersion(stackFiles, stack, matchPartOfStackName=matchPartOfStackName)
        resolvedStackFiles.append(resolvedStackFile)

    return resolvedStackFiles


def GetResolvedStackFileVersion(stackFiles: list, stack: str, matchPartOfStackName = False):
    resolvedStackFile = None
    newestVersion = None
    for stackFile in stackFiles:
        stackName, version = GetStackNameAndVersionFromStackFile(stackFile)

        spec = GetVersionSpecification(stack)
        if ((matchPartOfStackName and spec.name in stackName) or spec.name == stackName) and MatchVersionSpecification(spec.specs, version):
            if newestVersion is None or version > newestVersion:
                resolvedStackFile = stackFile
                newestVersion = version

    if resolvedStackFile is None:
        raise Exception("Could not find a corresponding stack file for stack {0}.".format(stack))

    return resolvedStackFile


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


def GetVersionSpecification(stack: str):
    for req in requirements.parse(stack):
        # Returns name and version as req.name, req.specs
        return req


def GetStackNamesFromStackFiles(stackFiles: list):
    stacks = []
    for stackFile in stackFiles:
        stack = GetStackNameFromStackFile(stackFile)
        if not(stack in stacks):
            stacks.append(stack)

    return stacks


def GetStackNameFromStackFile(stackFile: str):
    stackName, version = GetStackNameAndVersionFromStackFile(stackFile)
    return stackName


def GetStackNameAndVersionFromStackFile(stackFile: str):
    stackFileBasename = os.path.basename(stackFile)
    stackName = stackFileBasename[stackFileBasename.find('docker-compose.') + 15:stackFileBasename.rfind('.')]
    matches = re.search('.[0-9]+', stackName)
    version = None
    if matches:
        versionStr = stackName[matches.span()[0]+1:]
        version = semantic_version.Version(versionStr)
        stackName = stackName[:matches.span()[0]]

    return (stackName, version)