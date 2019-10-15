import argparse
import warnings
import os
from dotenv import load_dotenv
from DockerFeed.StackHandler import StackHandler
from DockerFeed.ArtifactStore import ArtifactStore

DEFAULT_URI = 'https://artifacts/'
DEFAULT_FEED = 'docker-delivery'
PACKAGE_CONSOLE_NAME = 'DockerFeed'
DEFAULT_LOGS_FOLDER = 'logs'

def Main(args = None, stackHandler: StackHandler = None, artifactStore: ArtifactStore = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, nargs='+',
                        help="Initialize swarm with 'init', \r\n"
                             + "deploy stacks with 'deploy', \r\n"
                             + "remove stacks with 'rm/remove', \r\n"
                             + "list stacks with 'ls/list', \r\n"
                             + "prune all stacks with 'prune', \r\n"
                             + "pull stacks with 'pull', \r\n"
                             + "push stacks with 'push'. \r\n"
                             + "run stacks as batch processes with 'run'. \r\n"
                             + "verify stacks with 'verify'. \r\n"
                             + "Append stacks to handle following the action. \r\n"
                             + "If no stacks are provided, then all stacks are deployed/removed. \r\n"
                             + "Example: '{0} deploy stack1 stack2' \r\n".format(PACKAGE_CONSOLE_NAME))

    parser.add_argument("-u", "--user", type=str, help="Specify user credentials for jfrog as <user>:<password>.", default=None)
    parser.add_argument("-t", "--token", type=str, help="Specify token for jfrog.", default=None)
    parser.add_argument("-f", "--feed", type=str, help="Specify jfrog feed. Default is '{0}'".format(DEFAULT_FEED), default=DEFAULT_FEED)
    parser.add_argument("-s", "--storage", type=str, help="Specify storage folder to use for local storage of compose files.", default=None)
    parser.add_argument("-e", "--env", type=str, nargs='+', help="Add environment variables to expose as <envKey=envValue>. "
                                                                 "A present '.env' file will be handled as an environment file to expose.", default=[])
    parser.add_argument("--ignored-stacks", type=str, nargs='+', help="Add a list of stacks to ignore.", default=[])
    parser.add_argument("--uri", type=str, help="Specify jfrog uri. Default is {0}".format(DEFAULT_URI), default=DEFAULT_URI)
    parser.add_argument("--logs-folder", type=str, help="Specify folder for storing log files when executing batch processes with 'run'. Default is './{0}'.".format(DEFAULT_LOGS_FOLDER), default=None)
    parser.add_argument("--no-logs", help="Add --no-logs to drop storing log files when executing batch processes with 'run'.", action='store_true')
    parser.add_argument("--offline", help="Add --offline to work offline.", action='store_true')
    parser.add_argument("--remove-files", help="Add --remove-files to remove files from local storage when removing stacks.", action='store_true')
    parser.add_argument("--verify-uri", help="Add --verify-uri to verify jfrog uri certificate.", action='store_true')
    parser.add_argument("--verify-stacks-on-deploy", help="Add --verify-stacks-on-deploy to deploy only valid stacks.", action='store_true')
    parser.add_argument("--verify-images", help="Add --verify-images to validate required labels on images.", action='store_true')
    parser.add_argument("--verify-no-configs", help="Add --verify-no-configs to validate that no Swarm configs are used in stack.", action='store_true')
    parser.add_argument("--verify-no-secrets", help="Add --verify-no-secrets to validate that no Swarm secrets are used in stack.", action='store_true')
    parser.add_argument("--verify-no-volumes", help="Add --verify-no-volumes to validate that no Swarm volumes are used in stack.", action='store_true')
    parser.add_argument("--verify-no-ports", help="Add --verify-no-ports to validate that no ports are exposed in stack.", action='store_true')
    parser.add_argument("-i", "--infrastructure", type=str, nargs='+', help="Specify infrastructure stacks to use. Default is ['infrastructure'].", default=['infrastructure'])
    args = parser.parse_args(args)

    action = args.action[0]
    stacks = None
    if len(args.action) > 1:
        stacks = args.action[1:]

    username = ParseUsernameAndPassword(args.user)[0]
    password = ParseUsernameAndPassword(args.user)[1]
    token = args.token
    feed = args.feed
    storage = args.storage
    logsFolder = args.logs_folder
    noLogs = args.no_logs
    envVariables = args.env
    ignoredStacks = args.ignored_stacks
    uri = args.uri
    offline = args.offline
    removeFiles = args.remove_files
    verifyUri = args.verify_uri
    verifyStacksOnDeploy = args.verify_stacks_on_deploy
    verifyImages = args.verify_images
    verifyNoConfigs = args.verify_no_configs
    verifyNoSecrets = args.verify_no_secrets
    verifyNoVolumes = args.verify_no_volumes
    verifyNoPorts = args.verify_no_ports
    infrastructureStacks = args.infrastructure

    ExposeEnvironmentVariables(envVariables)

    if os.path.isfile('.env'):
        load_dotenv('.env')

    moduleDir = os.path.dirname(os.path.realpath(__file__))
    load_dotenv(os.path.join(moduleDir, 'default.env'))
    if storage is None:
        stacksFolder = os.path.join(moduleDir, 'stacks')
    else:
        stacksFolder = os.path.join(os.getcwd(), storage)

    if logsFolder is None:
        logsFolder = os.path.join(os.getcwd(), DEFAULT_LOGS_FOLDER)

    if artifactStore is None:
        artifactStore = ArtifactStore(
            username=username,
            password=password,
            apiKey=token,
            feed=feed,
            uri=uri,
            verifyCertificate=verifyUri)

    if stackHandler is None:
        stackHandler = StackHandler(artifactStore,
                                    stacksFolder=stacksFolder,
                                    logsFolder=logsFolder,
                                    noLogs=noLogs,
                                    infrastructureStacks=infrastructureStacks,
                                    ignoredStacks=ignoredStacks,
                                    offline=offline,
                                    removeFiles=removeFiles,
                                    verifyImages=verifyImages,
                                    verifyNoConfigs=verifyNoConfigs,
                                    verifyNoSecrets=verifyNoSecrets,
                                    verifyNoVolumes=verifyNoVolumes,
                                    verifyNoPorts=verifyNoPorts)

    feedUri = artifactStore.GetFeedUri()
    HandleAction(action, stacks, feedUri, offline, stacksFolder, stackHandler, verifyStacksOnDeploy)


def HandleAction(action, stacks, feedUri, offline, stacksFolder, stackHandler: StackHandler, verifyStacksOnDeploy):
    if action == 'init':
        stackHandler.Init()
    elif action == 'deploy':
        stackHandler.Deploy(stacks, verifyStacksOnDeploy=verifyStacksOnDeploy)
    elif action == 'rm' or action == 'remove':
        stackHandler.Remove(stacks)
    elif action == 'ls' or action == 'list':
        PrettyPrintStacks(stackHandler.List(stacks), feedUri, offline, stacksFolder)
    elif action == 'prune':
        stackHandler.Prune()
    elif action == 'pull':
        stackHandler.Pull(stacks)
    elif action == 'push':
        if stacks is None:
            warnings.warn('Please provide stacks to push.')
        else:
            stackHandler.Push(stacks)
    elif action == 'run':
        if not(stackHandler.Run(stacks)):
            raise Exception("Some stacks failed execution! See warnings in log.")
    elif action == 'verify':
        if not(stackHandler.Verify(stacks)):
            raise Exception("Stacks failed verification! See warnings in log.")
    else:
        warnings.warn("No action provided, please add -help to get help.")


def ParseUsernameAndPassword(usernameAndPassword: str):
    if usernameAndPassword is None:
        return [None, None]
    elif not(':' in usernameAndPassword):
        warnings.warn('Cannot parse username and password {0}. It should be of form <user>:<password>'.format(usernameAndPassword))
        return [None, None]
    return usernameAndPassword.split(':')


def ExposeEnvironmentVariables(envVariables):
    for envVariable in envVariables:
        if not('=' in envVariable):
            warnings.warn('Cannot parse environment variable {0}. It should be of form <envKey>=<envValue>'.format(envVariable))
        else:
            key = envVariable.split('=')[0]
            value = envVariable.split('=')[1]
            os.environ[key] = value


def PrettyPrintStacks(stacks, feedUrl, offline, stacksFolder):
    if offline:
        info = "<--- Stacks in local folder {0} --->\r\n".format(stacksFolder)
    else:
        info = "<--- Stacks on feed {0} --->\r\n".format(feedUrl)
    for stack in stacks:
        info += stack + '\r\n'

    print(info)
    return info