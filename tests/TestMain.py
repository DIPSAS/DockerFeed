import unittest
import os
from tests import TestUtilities
from DockerBuildSystem import DockerComposeTools
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

    def test_RunStacks(self):
        DockerComposeTools.DockerComposeBuild(["tests/testBatchStacks/docker-compose.batch.yml"])
        defaultArgs = ['--storage', 'tests/testBatchStacks', '--user', 'dummy:password', '--offline']
        self.assertTrue(os.path.isdir('tests/testBatchStacks'))

        args = ['init'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        os.environ['SHOULD_FAIL'] = 'false'
        os.environ['SHOULD_FAIL_2'] = 'false'
        args = ['run'] + defaultArgs
        Main.Main(args)

        os.environ['SHOULD_FAIL'] = 'true'
        os.environ['SHOULD_FAIL_2'] = 'false'
        args = ['run'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)


    def test_DeployStacksWithFile(self):
        defaultArgs = ['--storage', 'tests/testStacks', '--user', 'dummy:password', '--offline', '-r', 'tests/testStacks/stackList.txt']
        self.assertTrue(os.path.isdir('tests/testStacks'))
        args = ['prune'] + defaultArgs
        Main.Main(args)

        args = ['init'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['deploy'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        TestUtilities.AssertStacksExists(['nginx_test_digest'], False)

        args = ['prune'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], False)
        TestUtilities.AssertStacksExists(['nginx_test_digest'], False)
        TestUtilities.AssertInfrastructureExists(False)

    def test_DeployStacksWithSwarmManagementFile(self):
        defaultArgs = ['--storage', './', '--user', 'dummy:password', '--offline']
        self.assertTrue(os.path.isdir('tests/testStacksWithSwarmManagement'))
        cwd = os.getcwd()
        os.chdir('tests/testStacksWithSwarmManagement')
        try:
            args = ['prune'] + defaultArgs
            Main.Main(args)

            args = ['init'] + defaultArgs
            Main.Main(args)
            TestUtilities.AssertInfrastructureExists(True, "infrastructure_test_swm_network")

            args = ['deploy'] + defaultArgs
            Main.Main(args)
            TestUtilities.AssertStacksExists(['nginx_test'], True)

            args = ['prune'] + defaultArgs
            Main.Main(args)
            TestUtilities.AssertStacksExists(['nginx_test'], False)
        finally:
            os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()