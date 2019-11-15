from DockerFeed.Handlers.StackHandler import StackHandler
from DockerBuildSystem import YamlTools


def DeployModule(stackHandler: StackHandler, moduleFile):
    yamlData: dict = YamlTools.GetYamlData([moduleFile])
    modules = yamlData.get('modules', [])
    for module in modules:
        moduleData: dict = yamlData['modules'][module]

        if 'run' in moduleData:
            stackHandler.Run(moduleData['run'])

        if 'deploy' in moduleData:
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
