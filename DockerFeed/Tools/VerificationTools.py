from DockerBuildSystem import DockerImageTools
import warnings


def VerifyImageDigest(stackFile: str, service: str, imageName: str):
    if not('@sha256:' in imageName):
        warnings.warn('Missing image digest on service {0} in stack file {1}'.format(service, stackFile))
        return False
    return True


def VerifyImage(imageName: str, requiredImageLabels: list):
    DockerImageTools.PullImage(imageName)
    valid = True
    for requiredImageLabel in requiredImageLabels:
        valid &= VerifyImageLabelExists(imageName, requiredImageLabel)
    return valid


def VerifyImageLabelExists(imageName: str, label: str):
    if not(DockerImageTools.CheckImageLabelExists(imageName, label)):
        warnings.warn('Missing label {0} on image {1}'.format(label, imageName))
        return False
    return True


def VerifyNoConfigs(yamlData: dict, service: str):
    if 'configs' in yamlData or 'configs' in yamlData['services'][service]:
        warnings.warn('Invalid configs detected in service {0}'.format(service))
        return False
    return True


def VerifyNoSecrets(yamlData: dict, service: str):
    if 'secrets' in yamlData or 'secrets' in yamlData['services'][service]:
        warnings.warn('Invalid secrets detected in service {0}'.format(service))
        return False
    return True


def VerifyNoVolumes(yamlData: dict, service: str):
    if 'volumes' in yamlData or 'volumes' in yamlData['services'][service]:
        warnings.warn('Invalid volumes detected in service {0}'.format(service))
        return False
    return True


def VerifyNoPorts(yamlData: dict, service: str):
    if 'ports' in yamlData['services'][service]:
        warnings.warn('Invalid ports detected in service {0}'.format(service))
        return False
    return True
