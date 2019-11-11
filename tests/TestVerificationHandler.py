import unittest
from DockerFeed.VerificationHandler import VerificationHandler

class TestVerificationHandler(unittest.TestCase):

    def test_VerifyComposeFiles(self):
        requiredImageLabels = ['maintainer']
        composeFile = "tests/testStacks/docker-compose.nginx_test_digest.1.1.0.yml"
        verificationHandler = VerificationHandler(requiredImageLabels=requiredImageLabels)
        self.assertTrue(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_MissingDigest(self):
        requiredImageLabels = ['maintainer']
        composeFile = "tests/testStacks/docker-compose.nginx_test.1.0.0.yml"
        verificationHandler = VerificationHandler(requiredImageLabels=requiredImageLabels)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_MissingLabels(self):
        requiredImageLabels = ['non_existent']
        composeFile = "tests/testStacks/docker-compose.nginx_test_digest.1.1.0.yml"
        verificationHandler = VerificationHandler(requiredImageLabels=requiredImageLabels)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_InvalidConfigs(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_config.1.0.0.yml"
        verificationHandler = VerificationHandler(verifyImages=False)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_InvalidSecrets(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_secret.1.0.0.yml"
        verificationHandler = VerificationHandler(verifyImages=False)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_InvalidVolumes(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_volume.1.0.0.yml"
        verificationHandler = VerificationHandler(verifyImages=False)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))

    def test_VerifyComposeFiles_InvalidPorts(self):
        composeFile = "tests/invalidTestStacks/docker-compose.nginx_test_invalid_port.1.0.0.yml"
        verificationHandler = VerificationHandler(verifyImages=False)
        self.assertFalse(verificationHandler.VerifyStackFile(composeFile))




if __name__ == '__main__':
    unittest.main()