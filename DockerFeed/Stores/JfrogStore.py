import os
import getpass
from artifactory import ArtifactoryPath
import requests.packages.urllib3 as urllib3
from DockerFeed.Stores.AbstractStore import AbstractStore

class JfrogStore(AbstractStore):
    def __init__(self, \
                 username = None, \
                 password = None, \
                 apiKey = None,
                 uri = 'https://artifacts/delivery-dev', \
                 verifyCertificate = False):

        self.__uri = uri
        self.__username = username
        self.__password = password
        self.__apiKey = apiKey
        self.__verifyCertificate = verifyCertificate

        if not(self.__verifyCertificate):
            urllib3.disable_warnings()


    def GetSource(self):
        return self.__uri


    def Pull(self, artifactName, outputFolder):
        with self.__CreateArtifactoryPath(artifactName) as path:
            with path.open() as f:
                with open(os.path.join(outputFolder, artifactName), "wb") as out:
                    out.write(f.read())


    def Push(self, artifactFile):
        if not(os.path.isfile(artifactFile)):
            raise Exception('Artifact file {0} does not exist!'.format(artifactFile))

        with self.__CreateArtifactoryPath() as path:
            path.deploy_file(artifactFile)


    def Exists(self, artifactName):
        with self.__CreateArtifactoryPath(artifactName) as path:
            return path.exists()


    def Remove(self, artifactName):
        with self.__CreateArtifactoryPath(artifactName) as path:
            if path.exists():
                path.unlink()


    def List(self):
        artifacts = []
        with self.__CreateArtifactoryPath() as path:
            for artifact in path:
                artifacts.append(str(artifact))

        return artifacts


    def __CreateArtifactoryPath(self, path=None):
        uri = self.__uri
        if not(path is None):
            uri += '/' + path

        if self.__apiKey is None:
            self.__RequestCredentials()
            path = ArtifactoryPath(uri, auth=(self.__username, self.__password), verify=self.__verifyCertificate)
        else:
            path = ArtifactoryPath(uri, apikey=self.__apiKey, verify=self.__verifyCertificate)
        return path


    def __RequestCredentials(self):
        if self.__apiKey is None and self.__username is None:
            self.__username = input('Username: ')

        if self.__apiKey is None and self.__password is None:
            self.__password = getpass.getpass()