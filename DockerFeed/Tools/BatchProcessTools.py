import warnings
import random
import os
from datetime import datetime
from DockerFeed.Tools import StackVersionTools
from DockerBuildSystem import DockerImageTools, YamlTools, DockerComposeTools


def ExecuteStackAsProcess(stackFile: str, stacksFolder: str, noLogs: bool, logsFolder: str):
    stackName, version, stackFileIsValid = StackVersionTools.GetStackNameAndVersionFromStackFile(stackFile)
    if not(stackFileIsValid):
        exitCode = 0
        return exitCode

    temporaryStackFile = __GenerateStackFileWithContainerNames(stackFile, stackName, stacksFolder)
    try:
        DockerComposeTools.DockerComposeUp([temporaryStackFile])
        exitCode = __VerifyStackExecutedSuccessfully(temporaryStackFile, stackName, noLogs, logsFolder)
        DockerComposeTools.DockerComposeDown([temporaryStackFile])
    finally:
        os.remove(temporaryStackFile)
    if exitCode > 0:
        warnings.warn("Stack '" + stackName + "' FAILED!")
    else:
        print(stackName + " stack finished with success.")

    return exitCode


def __GenerateStackFileWithContainerNames(stackFile: str, stackName: str, stacksFolder: str):
    yamlData: dict = YamlTools.GetYamlData([stackFile])

    random.seed()
    randomId = random.randint(0, 1000)
    prefix = stackName + "_"
    subfix = "_" + str(randomId)
    DockerComposeTools.AddContainerNames(yamlData, prefix=prefix, subfix=subfix)
    temporaryStackFile = os.path.join(stacksFolder, "docker-compose-temp.{0}.{1}.yml".format(stackName, randomId))
    YamlTools.DumpYamlDataToFile(yamlData, temporaryStackFile)
    return temporaryStackFile


def __VerifyStackExecutedSuccessfully(temporaryStackFile: str, stackName: str, noLogs: bool, logsFolder: str):
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
            __WriteLogsFromContainerToFile(containerName, service, stackName, logsFolder)
        sumExitCodes += exitCode
        if exitCode > 0:
            warnings.warn("Container '" + containerName + "' FAILED!")
        else:
            print(containerName + " container finished with success.")

    return sumExitCodes


def __WriteLogsFromContainerToFile(containerName: str, service: str, stackName: str, logsFolder: str):
    logs = DockerImageTools.GetLogsFromContainer(containerName)
    dateTimeNow = datetime.now()
    timestampStr = dateTimeNow.strftime("%Y%m%dT%H%M%S")
    os.makedirs(logsFolder, exist_ok=True)
    logFile = os.path.join(logsFolder, "{0}.{1}.{2}-{3}.log".format(stackName, service, containerName, timestampStr))
    with open(logFile, "a+") as f:
        f.write(logs)