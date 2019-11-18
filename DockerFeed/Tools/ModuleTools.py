from DockerFeed.Handlers.StackHandler import StackHandler
from DockerBuildSystem import YamlTools
import warnings
import os


def DeployModule(stackHandler: StackHandler, moduleFile):
    yamlData: dict = YamlTools.GetYamlData([moduleFile])
    modules = yamlData.get('modules', [])
    for module in modules:
        moduleData: dict = yamlData['modules'][module]

        batchProcessesRanWithSuccess = True
        if 'run' in moduleData:
            batchProcessesRanWithSuccess = stackHandler.Run(moduleData['run'])

        if not(batchProcessesRanWithSuccess):
            baseFilename = os.path.basename(moduleFile)
            warnings.warn("Some of the batch processes of the {0} module in module artifact {1} failed! See warnings in log.".format(module, baseFilename))

        if 'deploy' in moduleData and batchProcessesRanWithSuccess:
            stackHandler.Deploy(moduleData['deploy'])


def RemoveModule(stackHandler: StackHandler, moduleFile):
    yamlData: dict = YamlTools.GetYamlData([moduleFile])
    modules = yamlData.get('modules', [])
    for module in modules:
        moduleData: dict = yamlData['modules'][module]

        if 'deploy' in moduleData:
            stackHandler.Remove(moduleData['deploy'])


def VerifyModule(stackHandler: StackHandler, moduleFile):
    yamlData: dict = YamlTools.GetYamlData([moduleFile])
    modules = yamlData.get('modules', [])
    valid = True
    for module in modules:
        moduleData: dict = yamlData['modules'][module]

        if 'run' in moduleData:
            valid &= stackHandler.Verify(moduleData['run'])

        if 'deploy' in moduleData:
            valid &= stackHandler.Verify(moduleData['deploy'])

    return valid
