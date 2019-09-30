import unittest
from DockerFeed import InfrastructureHandler
from tests import TestUtilities

class TestInfrastructureHandler(unittest.TestCase):

    def test_CreateRemoveInfrastructure(self):
        infrastructureFile = "tests/testStacks/docker-compose.infrastructure.yml"
        InfrastructureHandler.CreateInfrastructure(infrastructureFile)
        TestUtilities.AssertInfrastructureExists(True)
        InfrastructureHandler.RemoveInfrastructure(infrastructureFile)
        TestUtilities.AssertInfrastructureExists(False)


if __name__ == '__main__':
    unittest.main()