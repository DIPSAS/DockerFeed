import argparse
import os

DEFAULT_SOURCE = 'https://artifacts/delivery-dev'
PACKAGE_CONSOLE_NAME = 'DockerFeed'
DEFAULT_CACHE_FOLDER = os.path.join(os.path.expanduser('~'), '.dockerfeed', 'cache', 'stacks')
DEFAULT_LOGS_FOLDER = os.path.join(os.getcwd(), 'logs')
DEFAULT_PULL_STACKS_DESTINATION_FOLDER = os.path.join(os.getcwd(), 'stacks')


def ParseArguments(args = None):
    parser = argparse.ArgumentParser()
    __AddStackHandlerArguments(parser)
    __AddStoreArguments(parser)
    __AddVerificationHandlerArguments(parser)
    arguments = parser.parse_args(args)
    return arguments


def __AddStackHandlerArguments(parser: argparse.ArgumentParser):
    parser.add_argument("action", type=str, nargs='+',
                        help="Initialize swarm with 'init', \r\n"
                             + "deploy stacks with 'deploy', \r\n"
                             + "remove stacks with 'rm/remove', \r\n"
                             + "list stacks with 'ls/list', \r\n"
                             + "prune all stacks with 'prune', \r\n"
                             + "pull stacks with 'pull' to a local folder, \r\n"
                             + "push stacks with 'push'. \r\n"
                             + "run stacks as batch processes with 'run'. \r\n"
                             + "verify stacks with 'verify'. \r\n"
                             + "Append stacks to handle following the action. \r\n"
                             + "If no stacks are provided, then all stacks are deployed/removed. \r\n"
                             + "Example: '{0} deploy stack1 stack2' \r\n".format(PACKAGE_CONSOLE_NAME))

    parser.add_argument("-e", "--env", type=str, nargs='+',
                        help="Add environment variables to expose as <envKey=envValue>. "
                             "A present '.env' file will be handled as an environment file to expose.", default=[])
    parser.add_argument("-r", "--read", type=str, nargs='+',
                        help="Add files with a list of stacks to handle. "
                             "Each line in the file should be the stack name to handle.", default=[])
    parser.add_argument("--ignored-stacks", type=str, nargs='+',
                        help="Add a list of stacks to ignore.", default=[])
    parser.add_argument("--logs-folder", type=str,
                        help="Specify folder for storing log files when executing batch processes with 'run'. "
                             "Default is './{0}'.".format(
                            DEFAULT_LOGS_FOLDER), default=DEFAULT_LOGS_FOLDER)
    parser.add_argument("--no-logs",
                        help="Add --no-logs to drop storing log files when executing batch processes with 'run'.",
                        action='store_true')
    parser.add_argument("--output-folder", type=str,
                        help="Specify destination folder for pulling stack files with 'pull'. "
                             "Default is './{0}'.".format(
                            DEFAULT_PULL_STACKS_DESTINATION_FOLDER), default=DEFAULT_PULL_STACKS_DESTINATION_FOLDER)
    parser.add_argument("-i", "--infrastructure", type=str, nargs='+',
                        help="Specify path to swarm.management.yml files for creating the Swarm infrastructure.",
                        default=[])
    parser.add_argument("-c", "--cache", type=str,
                        help="Specify cache folder to use for local cache storage of stack files. "
                             "Default is {0}".format(
                            DEFAULT_CACHE_FOLDER), default=DEFAULT_CACHE_FOLDER)


def __AddStoreArguments(parser: argparse.ArgumentParser):
    parser.add_argument("-u", "--user", type=str,
                        help="Specify user credentials for jfrog as <user>:<password>.", default=None)
    parser.add_argument("-t", "--token", type=str,
                        help="Specify token for jfrog.", default=None)
    parser.add_argument("-s", "--source", type=str,
                        help="Specify feed source. Either uri to jfrog feed, or a local folder with stack files. "
                             "Default is '{0}'".format(
                            DEFAULT_SOURCE), default=DEFAULT_SOURCE)
    parser.add_argument("--verify-uri",
                        help="Add --verify-uri to verify jfrog uri certificate.", action='store_true')


def __AddVerificationHandlerArguments(parser: argparse.ArgumentParser):
    parser.add_argument("--verify-stacks-on-deploy",
                        help="Add --verify-stacks-on-deploy to deploy only valid stacks.",
                        action='store_true')
    parser.add_argument("--verify-image-digests",
                        help="Add --verify-image-digests to validate that image digests are used.", action='store_true')
    parser.add_argument("--verify-images",
                        help="Add --verify-images to validate required labels on images.",
                        action='store_true')
    parser.add_argument("--verify-no-configs",
                        help="Add --verify-no-configs to validate that no Swarm configs are used in stack.",
                        action='store_true')
    parser.add_argument("--verify-no-secrets",
                        help="Add --verify-no-secrets to validate that no Swarm secrets are used in stack.",
                        action='store_true')
    parser.add_argument("--verify-no-volumes",
                        help="Add --verify-no-volumes to validate that no Swarm volumes are used in stack.",
                        action='store_true')
    parser.add_argument("--verify-no-ports",
                        help="Add --verify-no-ports to validate that no ports are exposed in stack.",
                        action='store_true')
