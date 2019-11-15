import os
import re
import semantic_version
import requirements


def GetResolvedStackFileVersions(stackFiles: list, stacks: list, artifactIdentifier = 'docker-compose.', matchPartOfStackName = False):
    if len(stacks) == 0:
        stacks = GetStackNamesFromStackFiles(stackFiles, artifactIdentifier=artifactIdentifier)

    resolvedStackFiles = []
    for stack in stacks:
        resolvedStackFile = GetResolvedStackFileVersion(stackFiles, stack, artifactIdentifier=artifactIdentifier, matchPartOfStackName=matchPartOfStackName)
        resolvedStackFiles.append(resolvedStackFile)

    return resolvedStackFiles


def GetResolvedStackFileVersion(stackFiles: list, stack: str, artifactIdentifier = 'docker-compose.', matchPartOfStackName = False):
    resolvedStackFile = None
    newestVersion = None
    for stackFile in stackFiles:
        stackName, version, stackFileIsValid = GetStackNameAndVersionFromStackFile(stackFile, artifactIdentifier=artifactIdentifier)
        if not(stackFileIsValid):
            continue

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


def GetStackNamesFromStackFiles(stackFiles: list, artifactIdentifier = 'docker-compose.'):
    stacks = []
    for stackFile in stackFiles:
        stackName, version, stackFileIsValid = GetStackNameAndVersionFromStackFile(stackFile, artifactIdentifier=artifactIdentifier)
        if not(stackFileIsValid):
            continue

        if not(stackName in stacks):
            stacks.append(stackName)

    return stacks


def GetStackNameAndVersionFromStackFile(stackFile: str, artifactIdentifier = 'docker-compose.'):
    stackFileBasename = os.path.basename(stackFile)
    stackName = stackFileBasename[stackFileBasename.find(artifactIdentifier) + len(artifactIdentifier):stackFileBasename.rfind('.')]
    matches = re.search('.[0-9]+', stackName)
    version = None
    stackFileIsValid = False
    if matches:
        stackFileIsValid = True
        versionStr = stackName[matches.span()[0]+1:]
        version = semantic_version.Version(versionStr)
        stackName = stackName[:matches.span()[0]]

    return (stackName, version, stackFileIsValid)