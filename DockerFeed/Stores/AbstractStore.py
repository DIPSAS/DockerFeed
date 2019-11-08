import abc

class AbstractStore(abc.ABC):

    @abc.abstractmethod
    def GetSource(self):
        pass

    @abc.abstractmethod
    def Pull(self, artifactName, outputFolder):
        pass

    @abc.abstractmethod
    def Push(self, artifactFile):
        pass

    @abc.abstractmethod
    def Exists(self, artifactName):
        pass

    @abc.abstractmethod
    def Remove(self, artifactName):
        pass

    @abc.abstractmethod
    def List(self):
        pass