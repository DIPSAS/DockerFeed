import validators

from DockerFeed.Tools import MainTools, SwarmInitTools
from DockerFeed.Handlers.StackHandler import StackHandler
from DockerFeed.Handlers.ModuleHandler import ModuleHandler
from DockerFeed.VerificationHandler import VerificationHandler
from DockerFeed.Stores.AbstractStore import AbstractStore
from DockerFeed.Stores.JfrogStore import JfrogStore
from DockerFeed.Stores.FolderStore import FolderStore


def CreateModuleHandler(arguments, stackHandler = None, abstractStore = None):
    envVariables = arguments.env
    ignoredModules = arguments.ignored
    outputFolder = arguments.output_folder
    swmInfrastructureFiles = arguments.infrastructure
    cacheFolder = arguments.cache

    SwarmInitTools.ExposeEnvironmentVariables(envVariables, swmInfrastructureFiles)

    if abstractStore is None:
        abstractStore: AbstractStore = __CreateStore(arguments)
    if stackHandler is None:
        stackHandler: StackHandler = CreateStackHandler(arguments, abstractStore=abstractStore)

    return ModuleHandler(abstractStore,
                         stackHandler,
                         swmInfrastructureFiles=swmInfrastructureFiles,
                         ignoredModules=ignoredModules,
                         cacheFolder=cacheFolder,
                         outputFolder=outputFolder)


def CreateStackHandler(arguments, abstractStore = None, verificationHandler = None):
    envVariables = arguments.env
    ignoredStacks = arguments.ignored
    logsFolder = arguments.logs_folder
    outputFolder = arguments.output_folder
    noLogs = arguments.no_logs
    swmInfrastructureFiles = arguments.infrastructure
    cacheFolder = arguments.cache
    verifyStacksOnDeploy = arguments.verify_stacks_on_deploy

    SwarmInitTools.ExposeEnvironmentVariables(envVariables, swmInfrastructureFiles)

    if abstractStore is None:
        abstractStore: AbstractStore = __CreateStore(arguments)
    if verificationHandler is None:
        verificationHandler: VerificationHandler = __CreateVerificationHandler(arguments)

    return StackHandler(abstractStore,
                        verificationHandler,
                        verifyStacksOnDeploy=verifyStacksOnDeploy,
                        swmInfrastructureFiles=swmInfrastructureFiles,
                        cacheFolder=cacheFolder,
                        logsFolder=logsFolder,
                        outputFolder=outputFolder,
                        noLogs=noLogs,
                        ignoredStacks=ignoredStacks)


def __CreateStore(arguments):
    username: str = MainTools.ParseUsernameAndPassword(arguments.user)[0]
    password: str = MainTools.ParseUsernameAndPassword(arguments.user)[1]
    token: str = arguments.token
    source: str = arguments.source
    verifyUri: bool = arguments.verify_uri

    if validators.url(source) or validators.domain(source) \
            or source.startswith('http:') or source.startswith('https:'):
        return JfrogStore(
            username=username,
            password=password,
            apiKey=token,
            uri=source,
            verifyCertificate=verifyUri)
    else:
        return FolderStore(sourceFolder=source)


def __CreateVerificationHandler(arguments):
    verifyImageDigests = arguments.verify_image_digests
    verifyImages = arguments.verify_images
    verifyNoConfigs = arguments.verify_no_configs
    verifyNoSecrets = arguments.verify_no_secrets
    verifyNoVolumes = arguments.verify_no_volumes
    verifyNoPorts = arguments.verify_no_ports
    return VerificationHandler(
        verifyImageDigests=verifyImageDigests,
        verifyImages=verifyImages,
        verifyNoConfigs=verifyNoConfigs,
        verifyNoSecrets=verifyNoSecrets,
        verifyNoVolumes=verifyNoVolumes,
        verifyNoPorts=verifyNoPorts)