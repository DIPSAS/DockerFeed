import unittest
import os
from tests import TestUtilities
from DockerFeed import Main

class TestMain(unittest.TestCase):

    def test_MainInitDeployPrune(self):
        stacksToIgnoreArgs = ['--ignored-stacks', 'nginx_test_ignored']
        defaultArgs = ['--storage', 'tests/testStacks', '--user', 'dummy:password', '--offline']
        self.assertTrue(os.path.isdir('tests/testStacks'))

        args = ['init'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['deploy', '--verify-stacks-on-deploy'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)

        args = ['deploy'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)

        args = ['prune'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], False)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)
        TestUtilities.AssertInfrastructureExists(False)

        args = ['ls'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)

        args = ['verify', 'nginx_test_digest'] + defaultArgs
        Main.Main(args)

        args = ['verify'] + defaultArgs + stacksToIgnoreArgs + ['nginx_test']
        Main.Main(args)

        args = ['verify', 'nginx_test_digest', '--verify-images'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)

        args = ['verify'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)

    def test_DeployWithVerifyStacks(self):
        defaultArgs = ['--storage', 'tests/invalidTestStacks', '--user', 'dummy:password', '--offline']
        args = ['init'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['deploy', '--verify-stacks-on-deploy', '--verify-no-configs', '--verify-no-secrets', '--verify-no-volumes', '--verify-no-ports'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_config'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_secret'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_volume'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_port'], False)

        args = ['prune'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(False)



if __name__ == '__main__':
    unittest.main()