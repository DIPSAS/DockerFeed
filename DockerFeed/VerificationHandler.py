from DockerBuildSystem import DockerImageTools, YamlTools
import warnings


DEFAULT_REQUIRED_IMAGE_LABELS = [
    'org.opencontainers.image.created',
    'org.opencontainers.image.authors',
    'org.opencontainers.image.revision',
    'org.opencontainers.image.version',
    'org.opencontainers.image.documentation',
    'org.opencontainers.image.title',
]


def VerifyComposeFile(composeFile: str, \
                       verifyImageDigest = True, \
                       verifyImages = True, \
                       verifyNoConfigs = True, \
                       verifyNoSecrets = True, \
                       verifyNoVolumes = True, \
                       requiredImageLabels = DEFAULT_REQUIRED_IMAGE_LABELS):
    yamlData = YamlTools.GetYamlData([composeFile])

    valid = True
    for service in yamlData.get('services', []):
        if not ('image' in yamlData['services'][service]):
            warnings.warn('Missing image in compose file: {0}'.format(composeFile))
            valid = False
            continue

        imageName = yamlData['services'][service]['image']

        if verifyImageDigest:
            valid &= __VerifyImageDigest(composeFile, service, imageName)

        if verifyImages:
            valid &= __VerifyImage(imageName, requiredImageLabels)

        if verifyNoConfigs:
            valid &= __VerifyNoConfigs(yamlData, service)

        if verifyNoSecrets:
            valid &= __VerifyNoSecrets(yamlData, service)

        if verifyNoVolumes:
            valid &= __VerifyNoVolumes(yamlData, service)

    return valid


def __VerifyImageDigest(composeFile: str, service: str, imageName: str):
    if not('@sha256:' in imageName):
        warnings.warn('Missing image digest on service {0} in compose file {1}'.format(service, composeFile))
        return False
    return True


def __VerifyImage(imageName: str, requiredImageLabels: list):
    DockerImageTools.PullImage(imageName)
    valid = True
    for requiredImageLabel in requiredImageLabels:
        valid &= __VerifyImageLabelExists(imageName, requiredImageLabel)
    return valid


def __VerifyImageLabelExists(imageName: str, label: str):
    if not(DockerImageTools.CheckImageLabelExists(imageName, label)):
        warnings.warn('Missing label {0} on image {1}'.format(label, imageName))
        return False
    return True


def __VerifyNoConfigs(yamlData: dict, service: str):
    return not('configs' in yamlData or 'configs' in yamlData['services'][service])


def __VerifyNoSecrets(yamlData: dict, service: str):
    return not('secrets' in yamlData or 'secrets' in yamlData['services'][service])


def __VerifyNoVolumes(yamlData: dict, service: str):
    return not('volumes' in yamlData or 'volumes' in yamlData['services'][service])
