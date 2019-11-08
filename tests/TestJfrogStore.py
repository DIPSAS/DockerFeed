import unittest
from DockerFeed.Stores.JfrogStore import JfrogStore

JFROG_USERNAME = '<replace_me>'
JFROG_PASSWORD = '<replace_me>'
JFROG_URI = 'https://artifacts/delivery-dev'

@unittest.skip("Uncomment this skip to test manually.")
class TestJfrogStore(unittest.TestCase):

    def test_1_Push(self):
        store = JfrogStore(JFROG_USERNAME, JFROG_PASSWORD, uri=JFROG_URI)
        store.Push('tests/testStacks/docker-compose.nginx_test.yml')

    def test_2_Pull(self):
        store = JfrogStore(JFROG_USERNAME, JFROG_PASSWORD, uri=JFROG_URI)
        store.Pull('docker-compose.nginx_test.yml', 'tests/testStacks')

    def test_3_Exists(self):
        store = JfrogStore(JFROG_USERNAME, JFROG_PASSWORD, uri=JFROG_URI)
        self.assertTrue(store.Exists('docker-compose.nginx_test.yml'))

    def test_4_PushInvalidInput(self):
        store = JfrogStore(JFROG_USERNAME, JFROG_PASSWORD, uri=JFROG_URI)
        self.assertRaises(Exception, store.Push, 'invalidFile.yml')

    def test_5_List(self):
        store = JfrogStore(JFROG_USERNAME, JFROG_PASSWORD, uri=JFROG_URI)
        artifacts = store.List()
        print(artifacts)
        self.assertGreater(len(artifacts), 0)


if __name__ == '__main__':
    unittest.main()