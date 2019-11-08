from DockerBuildSystem import YamlTools
import warnings
from DockerFeed.Tools import VerificationTools

DEFAULT_REQUIRED_IMAGE_LABELS = [
    'org.opencontainers.image.created',
    'org.opencontainers.image.authors',
    'org.opencontainers.image.revision',
    'org.opencontainers.image.version',
    'org.opencontainers.image.documentation',
    'org.opencontainers.image.title',
]

class VerificationHandler:
    def __init__(self,
                 verifyImageDigests=True,
                 verifyImages=True,
                 verifyNoConfigs=True,
                 verifyNoSecrets=True,
                 verifyNoVolumes=True,
                 verifyNoPorts=True,
                 requiredImageLabels=DEFAULT_REQUIRED_IMAGE_LABELS):
        self.__verifyImageDigests = verifyImageDigests
        self.__verifyImages = verifyImages
        self.__verifyNoConfigs = verifyNoConfigs
        self.__verifyNoSecrets = verifyNoSecrets
        self.__verifyNoVolumes = verifyNoVolumes
        self.__verifyNoPorts = verifyNoPorts
        self.__requiredImageLabels = requiredImageLabels


    def VerifyStackFile(self, stackFile: str):
        yamlData = YamlTools.GetYamlData([stackFile])

        valid = True
        for service in yamlData.get('services', []):
            if not ('image' in yamlData['services'][service]):
                warnings.warn('Missing image in compose file: {0}'.format(stackFile))
                valid = False
                continue

            imageName = yamlData['services'][service]['image']

            if self.__verifyImageDigests:
                valid &= VerificationTools.VerifyImageDigest(stackFile, service, imageName)

            if self.__verifyImages:
                valid &= VerificationTools.VerifyImage(imageName, self.__requiredImageLabels)

            if self.__verifyNoConfigs:
                valid &= VerificationTools.VerifyNoConfigs(yamlData, service)

            if self.__verifyNoSecrets:
                valid &= VerificationTools.VerifyNoSecrets(yamlData, service)

            if self.__verifyNoVolumes:
                valid &= VerificationTools.VerifyNoVolumes(yamlData, service)

            if self.__verifyNoPorts:
                valid &= VerificationTools.VerifyNoPorts(yamlData, service)

        return valid