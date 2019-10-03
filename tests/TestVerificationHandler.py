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




if __name__ == '__main__':
    unittest.main()