import unittest
import os
import shutil
from tests import TestUtilities
from DockerBuildSystem import DockerComposeTools
from DockerFeed import Main

class TestMain(unittest.TestCase):

    def test_MainInitDeployPrune(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        stacksToIgnoreArgs = ['--ignored-stacks', 'nginx_test_ignored']
        defaultArgs = ['--cache', cacheFolder, '--source', 'tests/testStacks', '--user', 'dummy:password', '-i', 'tests/testStacks/swarm.management.yml']
        self.assertTrue(os.path.isdir('tests/testStacks'))

        args = ['init'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['deploy', '-r', 'tests/testStacks/stackList.txt', '--verify-stacks-on-deploy'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)

        args = ['deploy', '-r', 'tests/testStacks/stackList.txt'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)

        args = ['prune'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], False)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)

        args = ['ls'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)

    def test_Verify(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        stacksToIgnoreArgs = ['--ignored-stacks', 'nginx_test_ignored']
        defaultArgs = ['-r', 'tests/testStacks/stackList.txt', '--cache', cacheFolder, '--source', 'tests/testStacks', '--user', 'dummy:password', '-i', 'tests/testStacks/swarm.management.yml']
        self.assertTrue(os.path.isdir('tests/testStacks'))

        args = ['verify', 'nginx_test_digest'] + defaultArgs
        Main.Main(args)

        args = ['verify'] + defaultArgs + stacksToIgnoreArgs + ['nginx_test']
        Main.Main(args)

        args = ['verify', 'nginx_test_digest', '--verify-images'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)

        args = ['verify', '--verify-image-digests'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)

    def test_DeployWithVerifyStacks(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        defaultArgs = ['--cache', cacheFolder, '--source', 'tests/invalidTestStacks', '--user', 'dummy:password', '-i', 'tests/invalidTestStacks/swarm.management.yml']
        args = ['init'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['deploy', '-r', 'tests/invalidTestStacks/stackList.txt', '--verify-stacks-on-deploy', '--verify-no-configs', '--verify-no-secrets', '--verify-no-volumes', '--verify-no-ports'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_config'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_secret'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_volume'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_port'], False)

        args = ['prune'] + defaultArgs
        Main.Main(args)

    def test_RunStacks(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        DockerComposeTools.DockerComposeBuild(["tests/testBatchStacks/docker-compose.batch.1.0.0.yml"])
        defaultArgs = ['--cache', cacheFolder, '--source', 'tests/testBatchStacks', '--user', 'dummy:password', '-i', 'tests/testBatchStacks/swarm.management.yml']
        self.assertTrue(os.path.isdir('tests/testBatchStacks'))

        args = ['init'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        os.environ['SHOULD_FAIL'] = 'false'
        os.environ['SHOULD_FAIL_2'] = 'false'
        args = ['run', 'batch'] + defaultArgs
        Main.Main(args)

        os.environ['SHOULD_FAIL'] = 'true'
        os.environ['SHOULD_FAIL_2'] = 'false'
        args = ['run', 'batch'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)


    def test_DeployStacksWithFile(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        defaultArgs = ['--cache', cacheFolder, '--source', 'tests/testStacks', '--user', 'dummy:password', '-r', 'tests/testStacks/stackList.txt', '-i', 'tests/testStacks/swarm.management.yml']
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


if __name__ == '__main__':
    unittest.main()