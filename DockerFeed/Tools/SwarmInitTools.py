from DockerBuildSystem import DockerSwarmTools
from SwarmManagement import SwarmManager, SwarmTools
from dotenv import load_dotenv
import os
import warnings


def ExposeEnvironmentVariables(envVariables: [], swmInfrastructureFiles: []):
    for envVariable in envVariables:
        if not('=' in envVariable):
            warnings.warn('Cannot parse environment variable {0}. It should be of form <envKey>=<envValue>'.format(envVariable))
        else:
            key = envVariable.split('=')[0]
            value = envVariable.split('=')[1]
            os.environ[key] = value

    if __CheckSwarmManagementYamlFileExists(yamlFiles=swmInfrastructureFiles):
        arguments = __GetSwarmManagementArgumentsWithInfrastructureFiles(swmInfrastructureFiles)
        SwarmTools.LoadEnvironmentVariables(arguments=arguments)

    if os.path.isfile('.env'):
        load_dotenv('.env')


def InitWithSwarmManager(swmInfrastructureFiles: []):
    if not(__CheckSwarmManagementYamlFileExists(yamlFiles=swmInfrastructureFiles)):
        DockerSwarmTools.StartSwarm()
        return
    arguments = __GetSwarmManagementArgumentsWithInfrastructureFiles(swmInfrastructureFiles)
    SwarmManager.StartSwarm(arguments=arguments)


def PruneWithSwarmManager(swmInfrastructureFiles: []):
    if not(__CheckSwarmManagementYamlFileExists(yamlFiles=swmInfrastructureFiles)):
        return
    arguments = __GetSwarmManagementArgumentsWithInfrastructureFiles(swmInfrastructureFiles)
    SwarmManager.StopSwarm(arguments=arguments)


def __CheckSwarmManagementYamlFileExists(yamlFiles: [], defaultYamlFiles=SwarmTools.DEFAULT_SWARM_MANAGEMENT_YAML_FILES):
    allPossibleYamlFiles = yamlFiles + defaultYamlFiles
    for yamlFile in allPossibleYamlFiles:
        if os.path.isfile(yamlFile):
            return True
    return False


def __GetSwarmManagementArgumentsWithInfrastructureFiles(swmInfrastructureFiles: []):
    arguments = []
    for swmInfrastructureFile in swmInfrastructureFiles:
        arguments += ['-f', swmInfrastructureFile]
    return arguments