import os
import warnings
import random
import glob
from datetime import datetime
from DockerBuildSystem import DockerImageTools, YamlTools, DockerComposeTools


def ParseStackNameFromComposeFilename(stackFile):
    stackFileBasename = os.path.basename(stackFile)
    stackName = stackFileBasename[stackFileBasename.find('docker-compose.') + 15:stackFileBasename.rfind('.')]
    return stackName


def GetStackFileMatches(stacksFolder: str, stack = None):
    if stack is None:
        stackFileMatches = glob.glob(os.path.join(stacksFolder, 'docker-compose.*.y*ml'))
    else:
        stackFileMatches = glob.glob(os.path.join(stacksFolder, 'docker-compose.{0}.y*ml'.format(stack)))

    if len(stackFileMatches) == 0 and not (stack is None):
        warnings.warn('Could not find any stack files matching stack with name {0} in folder {1}!'.format(stack, stacksFolder))
    elif len(stackFileMatches) == 0 and stack is None:
        warnings.warn('Could not find any stack files in folder {0}!'.format(stacksFolder))

    return stackFileMatches


def GetStackNames(stacks: list, stack = None):
    composeStackBaseNames = []
    for composeStackName in stacks:
        composeStackBaseName = os.path.basename(composeStackName)
        if 'docker-compose.' in composeStackBaseName:
            if stack is None or stack == ParseStackNameFromComposeFilename(composeStackBaseName):
                composeStackBaseNames.append(composeStackBaseName)

    return composeStackBaseNames


def ExecuteStackAsProcess(stackFile: str, stacksFolder: str, noLogs: bool, logsFolder: str):
    stackName = ParseStackNameFromComposeFilename(stackFile)
    temporaryStackFile = GenerateStackFileWithContainerNames(stackFile, stacksFolder)
    try:
        DockerComposeTools.DockerComposeUp([temporaryStackFile])
        exitCode = VerifyStackExecutedSuccessfully(temporaryStackFile, stackName, noLogs, logsFolder)
        DockerComposeTools.DockerComposeDown([temporaryStackFile])
    finally:
        os.remove(temporaryStackFile)
    if exitCode > 0:
        warnings.warn("Stack '" + stackName + "' FAILED!")
    else:
        print(stackName + " stack finished with success.")

    return exitCode


def GenerateStackFileWithContainerNames(stackFile: str, stacksFolder: str):
    yamlData: dict = YamlTools.GetYamlData([stackFile])
    stackName = ParseStackNameFromComposeFilename(stackFile)

    random.seed()
    randomId = random.randint(0, 1000)
    prefix = stackName + "_"
    subfix = "_" + str(randomId)
    DockerComposeTools.AddContainerNames(yamlData, prefix=prefix, subfix=subfix)
    temporaryStackFile = os.path.join(stacksFolder, "docker-compose-temp.{0}.{1}.yml".format(stackName, randomId))
    YamlTools.DumpYamlDataToFile(yamlData, temporaryStackFile)
    return temporaryStackFile


def VerifyStackExecutedSuccessfully(temporaryStackFile: str, stackName: str, noLogs: bool, logsFolder: str):
    yamlData: dict = YamlTools.GetYamlData([temporaryStackFile])

    sumExitCodes = 0
    services = yamlData.get('services', [])
    for service in services:
        if not('container_name' in yamlData['services'][service]):
            raise Exception(("Cannot check exit code for service {0} in stack {1} " +
                          "due to missing container name tag.").format(service, stackName))

        containerName = yamlData['services'][service]['container_name']
        exitCode = DockerImageTools.GetContainerExitCode(containerName)
        if not(noLogs):
            WriteLogsFromContainerToFile(containerName, service, stackName, logsFolder)
        sumExitCodes += exitCode
        if exitCode > 0:
            warnings.warn("Container '" + containerName + "' FAILED!")
        else:
            print(containerName + " container finished with success.")

    return sumExitCodes


def WriteLogsFromContainerToFile(containerName: str, service: str, stackName: str, logsFolder: str):
    logs = DockerImageTools.GetLogsFromContainer(containerName)
    dateTimeNow = datetime.now()
    timestampStr = dateTimeNow.strftime("%Y%m%dT%H%M%S")
    os.makedirs(logsFolder, exist_ok=True)
    logFile = os.path.join(logsFolder, "{0}.{1}.{2}-{3}.log".format(stackName, service, containerName, timestampStr))
    with open(logFile, "a+") as f:
        f.write(logs)