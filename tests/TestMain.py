import unittest
import os
from tests import TestUtilities
from DockerFeed import Main

class TestMain(unittest.TestCase):

    def test_MainInitDeployPrune(self):
        defaultArgs = ['--storage', 'tests/testStacks', '--user', 'dummy:password', '--offline']
        self.assertTrue(os.path.isdir('tests/testStacks'))

        args = ['init'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['deploy'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)

        args = ['prune'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], False)
        TestUtilities.AssertInfrastructureExists(False)

        args = ['ls'] + defaultArgs
        Main.Main(args)

        args = ['verify', 'nginx_test_digest'] + defaultArgs
        Main.Main(args)

        args = ['verify', 'nginx_test_digest', '--verify-images'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)

        args = ['verify'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)




if __name__ == '__main__':
    unittest.main()