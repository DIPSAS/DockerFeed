import unittest
from tests import TestUtilities

@unittest.skip("Uncomment this skip to test manually.")
class TestArtifactStore(unittest.TestCase):

    def test_Pull(self):
        store = TestUtilities.CreateArtifactStore()
        store.Pull('docker-compose.infrastructure2.yml', 'tests/testStacks')


    def test_Push(self):
        store = TestUtilities.CreateArtifactStore()
        store.Push('tests/testStacks/docker-compose.nginx_test.yml')


    def test_PushInvalidInput(self):
        store = TestUtilities.CreateArtifactStore()
        self.assertRaises(Exception, store.Push, 'invalidFile.yml')


    def test_List(self):
        store = TestUtilities.CreateArtifactStore()
        artifacts = store.List()
        print(artifacts)
        self.assertGreater(len(artifacts), 0)


if __name__ == '__main__':
    unittest.main()