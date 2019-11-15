from DockerFeed.Stores.FolderStore import FolderStore
from DockerFeed.Handlers.StackHandler import StackHandler
from DockerFeed.Handlers.ModuleHandler import ModuleHandler
from DockerFeed.VerificationHandler import VerificationHandler
import subprocess
import shutil


def CreateModuleHandler(swmInfrastructureFiles=["tests/testStacks/swarm.management,yml"],
                        source="tests/testStacks",
                        ignoredModules = [],
                        ignoredStacks = ['nginx_test_ignored'],
                        verifyStacksOnDeploy=False,
                        cacheFolder = 'tests/cacheFolder'):

    store = FolderStore(sourceFolder=source)
    stackHandler = CreateStackHandler(swmInfrastructureFiles,
                                                    source,
                                                    ignoredStacks,
                                                    verifyStacksOnDeploy,
                                                    cacheFolder)
    return ModuleHandler(store,
                         stackHandler,
                         swmInfrastructureFiles=swmInfrastructureFiles,
                         cacheFolder=cacheFolder,
                         ignoredModules=ignoredModules)


def CreateStackHandler(swmInfrastructureFiles=["tests/testStacks/swarm.management,yml"],
                       source="tests/testStacks",
                       ignoredStacks = ['nginx_test_ignored'],
                       verifyStacksOnDeploy=False,
                       cacheFolder = 'tests/cacheFolder'):

    store = FolderStore(sourceFolder=source)
    verificationHandler = VerificationHandler(verifyImages=False)
    shutil.rmtree(cacheFolder, ignore_errors=True)
    return StackHandler(store,
                        verificationHandler,
                        swmInfrastructureFiles=swmInfrastructureFiles,
                        cacheFolder=cacheFolder,
                        ignoredStacks=ignoredStacks,
                        verifyStacksOnDeploy=verifyStacksOnDeploy)


def AssertInfrastructureExists(expected = True, network = "infrastructure_test_network"):
    terminalCommand = "docker network ls"
    networkNames = str(subprocess.Popen(terminalCommand, stdout=subprocess.PIPE, shell=True).communicate()[0])
    actual = network in networkNames
    assert(actual == expected)


def AssertStacksExists(stackNames: list, expected=True):
    terminalCommand = "docker stack ls"
    runningStacks = str(subprocess.Popen(terminalCommand, stdout=subprocess.PIPE, shell=True).communicate()[0])
    for stackName in stackNames:
        actual = stackName in runningStacks
        assert (actual == expected)