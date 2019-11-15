import warnings
from DockerFeed.Handlers.AbstractHandler import AbstractHandler
from DockerFeed.Handlers.StackHandler import StackHandler
from DockerFeed.Handlers.ModuleHandler import ModuleHandler
from DockerFeed.Tools import MainTools, ArgumentTools


def Main(args = None, stackHandler: StackHandler = None, moduleHandler: ModuleHandler = None):
    arguments = ArgumentTools.ParseArguments(args)
    action, stacks, handler = MainTools.ResolveArguments(arguments, stackHandler, moduleHandler)
    HandleAction(action, stacks, handler)


def HandleAction(action: str, stacks: list, handler: AbstractHandler):
    if action == 'init':
        handler.Init()
    elif action == 'deploy':
        handler.Deploy(stacks)
    elif action == 'rm' or action == 'remove':
        handler.Remove(stacks)
    elif action == 'ls' or action == 'list':
        MainTools.PrettyPrintStacks(handler.List(stacks), handler.GetSource())
    elif action == 'prune':
        handler.Prune()
    elif action == 'pull':
        handler.Pull(stacks)
    elif action == 'push':
        handler.Push(stacks)
    elif action == 'run':
        if not(handler.Run(stacks)):
            raise Exception("Some stacks failed execution! See warnings in log.")
    elif action == 'verify':
        if not(handler.Verify(stacks)):
            raise Exception("Stacks failed verification! See warnings in log.")
    else:
        warnings.warn("No action provided, please add -help to get help.")
