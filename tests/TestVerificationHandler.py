import unittest
from DockerFeed.VerificationHandler import VerificationHandler

class TestVerificationHandler(unittest.TestCase):

    def test_VerifyComposeFiles(self):
        requiredImageLabels = ['maintainer']
        composeFile = "tests/testStacks/docker-compose.nginx_test_digest.yml"
        verificationHandler = VerificationHandler(requiredImageLabels=requiredImageLabels)
        self.assertTrue(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_MissingDigest(self):
        requiredImageLabels = ['maintainer']
        composeFile = "tests/testStacks/docker-compose.nginx_test.yml"
        verificationHandler = VerificationHandler(requiredImageLabels=requiredImageLabels)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_MissingLabels(self):
        requiredImageLabels = ['non_existent']
        composeFile = "tests/testStacks/docker-compose.nginx_test_digest.yml"
        verificationHandler = VerificationHandler(requiredImageLabels=requiredImageLabels)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_InvalidConfigs(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_config.yml"
        verificationHandler = VerificationHandler(verifyImages=False)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_InvalidSecrets(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_secret.yml"
        verificationHandler = VerificationHandler(verifyImages=False)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_InvalidVolumes(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_volume.yml"
        verificationHandler = VerificationHandler(verifyImages=False)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_InvalidPorts(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_port.yml"
        verificationHandler = VerificationHandler(verifyImages=False)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))




if __name__ == '__main__':
    unittest.main()