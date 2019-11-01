import warnings
import os
from dotenv import load_dotenv
from DockerFeed import StackTools
from SwarmManagement import SwarmTools


def ParseStackListFiles(stackListFiles: []):
    stacks = []
    for stackListFile in stackListFiles:
        with open(stackListFile, 'r') as f:
            for line in f:
                line = line\
                    .replace('\r', '')\
                    .replace('\n', '')\
                    .replace(' ', '')
                stacks.append(line)
    return stacks


def ParseUsernameAndPassword(usernameAndPassword: str):
    if usernameAndPassword is None:
        return [None, None]
    elif not(':' in usernameAndPassword):
        warnings.warn('Cannot parse username and password {0}. It should be of form <user>:<password>'.format(usernameAndPassword))
        return [None, None]
    return usernameAndPassword.split(':')


def ExposeEnvironmentVariables(envVariables: [], swmInfrastructureFiles: []):
    for envVariable in envVariables:
        if not('=' in envVariable):
            warnings.warn('Cannot parse environment variable {0}. It should be of form <envKey>=<envValue>'.format(envVariable))
        else:
            key = envVariable.split('=')[0]
            value = envVariable.split('=')[1]
            os.environ[key] = value

    if StackTools.CheckSwarmManagementYamlFileExists(yamlFiles=swmInfrastructureFiles):
        arguments = StackTools.GetSwarmManagementArgumentsWithInfrastructureFiles(swmInfrastructureFiles)
        SwarmTools.LoadEnvironmentVariables(arguments=arguments)

    if os.path.isfile('.env'):
        load_dotenv('.env')


def PrettyPrintStacks(stacks: [], feedUrl: str, offline: bool, stacksFolder: str):
    if offline:
        info = "<--- Stacks in local folder {0} --->\r\n".format(stacksFolder)
    else:
        info = "<--- Stacks on feed {0} --->\r\n".format(feedUrl)
    for stack in stacks:
        info += stack + '\r\n'

    print(info)
    return info