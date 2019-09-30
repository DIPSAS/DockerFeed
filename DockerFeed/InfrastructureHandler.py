from DockerBuildSystem import YamlTools, DockerSwarmTools
import subprocess
import time


def CreateInfrastructure(infrastructureFile: str):
    yamlData: dict = YamlTools.GetYamlData([infrastructureFile])
    networks = __GetNetworks(yamlData)
    for network in networks:
        '''TODO fix DockerSwarmTools to take external as parameter'''
        props = networks[network]
        encrypted = props.get('encrypted', True)
        DockerSwarmTools.CreateSwarmNetwork(network, encrypted=encrypted)


def RemoveInfrastructure(infrastructureFile: str, maxRetries = 20):
    yamlData: dict = YamlTools.GetYamlData([infrastructureFile])
    networks = __GetNetworks(yamlData)
    for network in networks:
        retries = 0
        while not(__TryRemoveNetwork(network)) and retries < maxRetries:
            time.sleep(1)
            retries += 1


def __GetNetworks(yamlData: dict):
    return yamlData.get("networks", [])


def __TryRemoveNetwork(network):
    DockerSwarmTools.RemoveSwarmNetwork(network)
    terminalCommand = "docker network ls"
    networkNames = str(subprocess.Popen(terminalCommand, stdout=subprocess.PIPE, shell=True).communicate()[0])
    notExists = not((" " + network + " ") in networkNames)
    return notExists