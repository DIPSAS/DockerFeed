import warnings
from DockerFeed.StackHandler import StackHandler
from DockerFeed import StackHandlerCreator
from DockerFeed.Tools import MainTools, ArgumentTools


def Main(args = None, stackHandler: StackHandler = None):
    arguments = ArgumentTools.ParseArguments(args)
    action = arguments.action[0]
    stackListFilesToRead = arguments.read

    stacks = []
    if len(arguments.action) > 1:
        stacks += arguments.action[1:]

    if len(stackListFilesToRead) > 0:
        stacks += MainTools.ParseStackListFiles(stackListFilesToRead)

    AssertStacksProvided(action, stacks)

    if stackHandler is None:
        stackHandler = StackHandlerCreator.CreateStackHandler(arguments)

    HandleAction(action, stacks, stackHandler)


def HandleAction(action: str, stacks: list, stackHandler: StackHandler):
    if action == 'init':
        stackHandler.Init()
    elif action == 'deploy':
        stackHandler.Deploy(stacks)
    elif action == 'rm' or action == 'remove':
        stackHandler.Remove(stacks)
    elif action == 'ls' or action == 'list':
        MainTools.PrettyPrintStacks(stackHandler.List(stacks), stackHandler.GetSource())
    elif action == 'prune':
        stackHandler.Prune()
    elif action == 'pull':
        stackHandler.Pull(stacks)
    elif action == 'push':
        stackHandler.Push(stacks)
    elif action == 'run':
        if not(stackHandler.Run(stacks)):
            raise Exception("Some stacks failed execution! See warnings in log.")
    elif action == 'verify':
        if not(stackHandler.Verify(stacks)):
            raise Exception("Stacks failed verification! See warnings in log.")
    else:
        warnings.warn("No action provided, please add -help to get help.")


def AssertStacksProvided(action: str, stacks: list):
    if action == 'init' or action == 'prune' or \
            action == 'ls' or action == 'list':
        return

    if len(stacks) == 0:
        warnings.warn("Please provide stacks to handle. \r\n"
                      "Example: \r\n"
                      "-> dockerf deploy stack1 stack2>=1.2.3 \r\n"
                      "-> dockerf deploy -r stackList.txt")
        exit(1)
