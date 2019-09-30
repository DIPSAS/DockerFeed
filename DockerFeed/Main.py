import argparse
import warnings
import os
from dotenv import load_dotenv
from DockerFeed.StackHandler import StackHandler
from DockerFeed.ArtifactStore import ArtifactStore

DEFAULT_URI = 'https://artifacts/'
DEFAULT_FEED = 'docker-delivery'
PACKAGE_CONSOLE_NAME = 'DockerFeed'

def Main(args = None, stackHandler: StackHandler = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, nargs='+',
                        help="Initialize swarm with 'init', \r\n"
                             + "deploy stacks with 'deploy', \r\n"
                             + "remove stacks with 'rm/remove', \r\n"
                             + "list stacks with 'ls/list', \r\n"
                             + "prune all stacks with 'prune', \r\n"
                             + "pull stacks with 'pull', \r\n"
                             + "push stacks with 'push'. \r\n"
                             + "Append stacks to handle following the action. \r\n"
                             + "If no stacks are provided, then all stacks are deployed/removed. \r\n"
                             + "Example: '{0} deploy stack1 stack2' \r\n".format(PACKAGE_CONSOLE_NAME))

    parser.add_argument("-u", "--user", type=str, help="Specify user credentials for jfrog as <user>:<password>.", default=None)
    parser.add_argument("-t", "--token", type=str, help="Specify token for jfrog.", default=None)
    parser.add_argument("-f", "--feed", type=str, help="Specify jfrog feed. Default is '{0}'".format(DEFAULT_FEED), default=DEFAULT_FEED)
    parser.add_argument("-s", "--storage", type=str, help="Specify storage folder to use for local storage of compose files.", default=None)
    parser.add_argument("-e", "--env", type=str, nargs='+', help="Add environment variables to expose as <envKey=envValue>. "
                                                                 "A present '.env' file will be handled as an environment file to expose.", default=[])
    parser.add_argument("--uri", type=str, help="Specify jfrog uri. Default is {0}".format(DEFAULT_URI), default=DEFAULT_URI)
    parser.add_argument("--offline", help="Add --offline to work offline.", action='store_true')
    parser.add_argument("--remove-files", help="Add --remove-files to remove files from local storage when removing stacks.", action='store_true')
    parser.add_argument("--verify-uri", help="Add --verify-uri to verify jfrog uri certificate.", action='store_true')
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
    envVariables = args.env
    uri = args.uri
    offline = args.offline
    removeFiles = args.remove_files
    verifyUri = args.verify_uri
    infrastructureStacks = args.infrastructure

    ExposeEnvironmentVariables(envVariables)

    if os.path.isfile('.env'):
        load_dotenv('.env')

    changeWorkingDirectory = False
    if storage is None:
        changeWorkingDirectory = True
        storage = 'stacks'

    if stackHandler is None:
        artifactStore = ArtifactStore(
            username=username,
            password=password,
            apiKey=token,
            feed=feed,
            uri=uri,
            verifyCertificate=verifyUri)

        stackHandler = StackHandler(artifactStore,
                                    stacksFolder=storage,
                                    infrastructureStacks=infrastructureStacks,
                                    offline=offline,
                                    removeFiles=removeFiles)

    cwd = os.getcwd()
    moduleDir = os.path.dirname(os.path.realpath(__file__))
    load_dotenv(os.path.join(moduleDir, 'default.env'))
    if changeWorkingDirectory and not(action == 'push'):
        os.chdir(moduleDir)

    feedUri = artifactStore.GetFeedUri()
    storageFolder = os.path.join(os.getcwd(), storage)
    try:
        HandleAction(action, stacks, feedUri, offline, storageFolder, stackHandler)
    finally:
        os.chdir(cwd)


def HandleAction(action, stacks, feedUri, offline, storageFolder, stackHandler: StackHandler):
    if action == 'init':
        stackHandler.Init()
    elif action == 'deploy':
        stackHandler.Deploy(stacks)
    elif action == 'rm' or action == 'remove':
        stackHandler.Remove(stacks)
    elif action == 'ls' or action == 'list':
        PrettyPrintStacks(stackHandler.List(stacks), feedUri, offline, storageFolder)
    elif action == 'prune':
        stackHandler.Prune()
    elif action == 'pull':
        stackHandler.Pull(stacks)
    elif action == 'push':
        if stacks is None:
            warnings.warn('Please provide stacks to push.')
        else:
            stackHandler.Push(stacks)
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


def PrettyPrintStacks(stacks, feedUrl, offline, storageFolder):
    if offline:
        info = "<--- Stacks in local folder {0} --->\r\n".format(storageFolder)
    else:
        info = "<--- Stacks on feed {0} --->\r\n".format(feedUrl)
    for stack in stacks:
        info += stack + '\r\n'

    print(info)
    return info