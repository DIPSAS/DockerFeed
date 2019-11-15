import warnings
from DockerFeed.Handlers.StackHandler import StackHandler
from DockerFeed.Handlers.ModuleHandler import ModuleHandler
from DockerFeed import HandlerCreator
from DockerFeed.Tools import MainTools


def ResolveArguments(arguments, stackHandler: StackHandler = None, moduleHandler: ModuleHandler = None):
    action = arguments.action[0]
    stackListFilesToRead = arguments.read
    stacks = []
    isModuleAction = action == 'module'

    if isModuleAction:
        if len(arguments.action) < 2:
            warnings.warn("Please provide an action to handle with the modules, such as 'deploy'.")
            exit(1)
        action = arguments.action[1]
        if len(arguments.action) > 2:
            stacks += arguments.action[2:]
        handler = moduleHandler
        if handler is None:
            handler = HandlerCreator.CreateModuleHandler(arguments, stackHandler)

    else:
        if len(arguments.action) > 1:
            stacks += arguments.action[1:]
        handler = stackHandler
        if handler is None:
            handler = HandlerCreator.CreateStackHandler(arguments)

    if len(stackListFilesToRead) > 0:
        stacks += MainTools.ParseStackListFiles(stackListFilesToRead)

    AssertStacksProvided(action, stacks, isModuleAction)

    return action, stacks, handler


def AssertStacksProvided(action: str, stacks: list, moduleAction: bool):
    if action == 'init' or action == 'prune' or \
            action == 'ls' or action == 'list':
        return

    typesToHandle = 'stacks'
    prefixAction = ''
    if moduleAction:
        typesToHandle = 'modules'
        prefixAction = 'module '

    if len(stacks) == 0:
        warnings.warn("Please provide {0} to handle. \r\n".format(typesToHandle) +
                      "Example: \r\n" +
                      "-> dockerf {0}deploy stack1 stack2>=1.2.3 \r\n".format(prefixAction) +
                      "-> dockerf {0}deploy -r stackList.txt".format(prefixAction))
        exit(1)


def ParseStackListFiles(stackListFiles: []):
    stacks = []
    for stackListFile in stackListFiles:
        with open(stackListFile, 'r') as f:
            for line in f:
                line = line\
                    .replace('\r', '')\
                    .replace('\n', '')\
                    .replace('\t', '')\
                    .replace(' ', '')
                if not(line == ''):
                    stacks.append(line)
    return stacks


def ParseUsernameAndPassword(usernameAndPassword: str):
    if usernameAndPassword is None:
        return [None, None]
    elif not(':' in usernameAndPassword):
        warnings.warn('Cannot parse username and password {0}. It should be of form <user>:<password>'.format(usernameAndPassword))
        return [None, None]
    return usernameAndPassword.split(':')


def PrettyPrintStacks(stacks: [], source: str):
    info = "<--- Stacks from source {0} --->\r\n".format(source)
    for stack in stacks:
        info += stack + '\r\n'

    print(info)
    return info