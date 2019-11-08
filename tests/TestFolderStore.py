import unittest
import shutil
from DockerFeed.Stores.FolderStore import FolderStore

TEST_FOLDER_STORE = 'tests/tempFolderStore'

class TestFolderStore(unittest.TestCase):

    def test_1_Push(self):
        store = FolderStore(TEST_FOLDER_STORE)
        store.Push('tests/testStacks/docker-compose.nginx_test.yml')

    def test_2_Pull(self):
        store = FolderStore(TEST_FOLDER_STORE)
        store.Pull('docker-compose.nginx_test.yml', 'tests/testStacks')

    def test_3_Exists(self):
        store = FolderStore(TEST_FOLDER_STORE)
        self.assertTrue(store.Exists('docker-compose.nginx_test.yml'))

    def test_4_PushInvalidInput(self):
        store = FolderStore(TEST_FOLDER_STORE)
        self.assertRaises(Exception, store.Push, 'invalidFile.yml')

    def test_5_List(self):
        store = FolderStore(TEST_FOLDER_STORE)
        artifacts = store.List()
        print(artifacts)
        self.assertGreater(len(artifacts), 0)

    def test_6_Remove(self):
        store = FolderStore(TEST_FOLDER_STORE)
        self.assertTrue(store.Exists('docker-compose.nginx_test.yml'))
        store.Remove('docker-compose.nginx_test.yml')
        self.assertFalse(store.Exists('docker-compose.nginx_test.yml'))
        shutil.rmtree(TEST_FOLDER_STORE)


if __name__ == '__main__':
    unittest.main()