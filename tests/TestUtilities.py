from DockerFeed.ArtifactStore import ArtifactStore
from DockerFeed.StackHandler import StackHandler
import subprocess
from unittest.mock import MagicMock

JFROG_USERNAME = '<replace_me>'
JFROG_PASSWORD = '<replace_me>'

def CreateArtifactStore(mock = False):
    if not(mock):
        return ArtifactStore(JFROG_USERNAME, JFROG_PASSWORD)

    mockStore = ArtifactStore(JFROG_USERNAME, JFROG_PASSWORD)
    mockStore.Pull = MagicMock(return_value=None)
    mockStore.List = MagicMock(return_value=['tests/testStacks/docker-compose.nginx_test_online.yml'])
    return mockStore

def CreateStackHandler(offline=False,
                       mockStore=True,
                       swmInfrastructureFiles=["tests/testStacks/swarm.management,yml"],
                       stacksFolder="tests/testStacks",
                       verifyImages=False,
                       ignoredStacks = ['nginx_test_ignored']):
    store = CreateArtifactStore(mockStore)
    return StackHandler(store,
                        swmInfrastructureFiles=swmInfrastructureFiles,
                        offline=offline,
                        stacksFolder=stacksFolder,
                        verifyImages=verifyImages,
                        ignoredStacks=ignoredStacks)


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