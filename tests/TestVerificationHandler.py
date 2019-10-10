import unittest
from DockerFeed import VerificationHandler

class TestVerificationHandler(unittest.TestCase):

    def test_VerifyComposeFiles(self):
        requiredImageLabels = ['maintainer']
        composeFile = "tests/testStacks/docker-compose.nginx_test_digest.yml"
        self.assertTrue(VerificationHandler.VerifyComposeFile(composeFile, requiredImageLabels=requiredImageLabels))

    def test_VerifyComposeFiles_MissingDigest(self):
        requiredImageLabels = ['maintainer']
        composeFile = "tests/testStacks/docker-compose.nginx_test.yml"
        self.assertFalse(VerificationHandler.VerifyComposeFile(composeFile, requiredImageLabels=requiredImageLabels))

    def test_VerifyComposeFiles_MissingLabels(self):
        requiredImageLabels = ['non_existent']
        composeFile = "tests/testStacks/docker-compose.nginx_test_digest.yml"
        self.assertFalse(VerificationHandler.VerifyComposeFile(composeFile, requiredImageLabels=requiredImageLabels))

    def test_VerifyComposeFiles_InvalidConfigs(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_config.yml"
        self.assertFalse(VerificationHandler.VerifyComposeFile(composeFile, verifyImages=False))

    def test_VerifyComposeFiles_InvalidSecrets(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_secret.yml"
        self.assertFalse(VerificationHandler.VerifyComposeFile(composeFile, verifyImages=False))

    def test_VerifyComposeFiles_InvalidVolumes(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_volume.yml"
        self.assertFalse(VerificationHandler.VerifyComposeFile(composeFile, verifyImages=False))

    def test_VerifyComposeFiles_InvalidPorts(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_port.yml"
        self.assertFalse(VerificationHandler.VerifyComposeFile(composeFile, verifyImages=False))




if __name__ == '__main__':
    unittest.main()