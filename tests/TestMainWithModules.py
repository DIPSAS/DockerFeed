import unittest
import os
import shutil
from tests import TestUtilities
from DockerFeed import Main

class TestMainWithModules(unittest.TestCase):

    def test_MainInitDeployPrune(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        stacksToIgnoreArgs = ['--ignored', 'nginx_test_ignored']
        defaultArgs = ['--cache', cacheFolder, '--source', 'tests/testStacks', '--user', 'dummy:password', '-i', 'tests/testStacks/swarm.management.yml']
        self.assertTrue(os.path.isdir('tests/testStacks'))

        args = ['module', 'init'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['module', 'deploy', '-r', 'tests/testStacks/stackList.txt', '--verify-stacks-on-deploy'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)

        args = ['module', 'deploy', '-r', 'tests/testStacks/stackList.txt'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)

        args = ['module', 'prune'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], False)
        TestUtilities.AssertStacksExists(['nginx_test_ignored'], False)

        args = ['module', 'ls'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)

    def test_Pull(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        stacksToIgnoreArgs = ['--ignored', 'nginx_test_ignored']
        defaultArgs = ['--cache', cacheFolder, '--source', 'tests/testStacks', '--user', 'dummy:password', '-i', 'tests/testStacks/swarm.management.yml']
        self.assertTrue(os.path.isdir('tests/testStacks'))

        outputFolder = 'tests/cacheFolder/pulledStacks'
        args = ['module', 'pull', '-r', 'tests/testStacks/stackList.txt', '--output-folder', outputFolder] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        self.assertTrue(os.path.isfile(os.path.join(outputFolder, 'docker-compose-module.nginx_test.1.1.1.yml')))


    def test_Push(self):
        cacheFolder = 'tests/cacheFolder'
        outputFolder = os.path.join(cacheFolder, 'pushedStacks')
        shutil.rmtree(cacheFolder, ignore_errors=True)
        self.assertTrue(os.path.isdir('tests/testStacks'))

        stacksToIgnoreArgs = ['--ignored', 'nginx_test_ignored']
        defaultArgs = ['--cache', cacheFolder, '--source', outputFolder, '--user', 'dummy:password', '-i', 'tests/testStacks/swarm.management.yml']

        args = ['module', 'push', 'tests/testStacks/docker-compose-module.*.yml'] + defaultArgs + stacksToIgnoreArgs
        Main.Main(args)
        self.assertTrue(os.path.isfile(os.path.join(outputFolder, 'docker-compose-module.nginx_test.1.0.0.yml')))
        self.assertTrue(os.path.isfile(os.path.join(outputFolder, 'docker-compose-module.nginx_test.1.1.1.yml')))


    def test_Verify(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        stacksToIgnoreArgs = ['--ignored', 'nginx_test_ignored']
        defaultArgs = ['-r', 'tests/testStacks/stackList.txt', '--cache', cacheFolder, '--source', 'tests/testStacks', '--user', 'dummy:password', '-i', 'tests/testStacks/swarm.management.yml']
        self.assertTrue(os.path.isdir('tests/testStacks'))

        args = ['module', 'verify', 'nginx_test_digest'] + defaultArgs
        Main.Main(args)

        args = ['module', 'verify'] + defaultArgs + stacksToIgnoreArgs + ['nginx_test']
        Main.Main(args)

        args = ['module', 'verify', 'nginx_test_digest', '--verify-images'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)

        args = ['module', 'verify', '--verify-image-digests'] + defaultArgs
        self.assertRaises(Exception, Main.Main, args)

    def test_DeployWithVerifyStacks(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        defaultArgs = ['--cache', cacheFolder, '--source', 'tests/invalidTestStacks', '--user', 'dummy:password', '-i', 'tests/invalidTestStacks/swarm.management.yml']
        args = ['module', 'init'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['module', 'deploy', 'nginx_test_invalid', '--verify-stacks-on-deploy', '--verify-no-configs', '--verify-no-secrets', '--verify-no-volumes', '--verify-no-ports'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_config'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_secret'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_volume'], False)
        TestUtilities.AssertStacksExists(['nginx_test_invalid_port'], False)

        args = ['module', 'prune'] + defaultArgs
        Main.Main(args)


    def test_DeployStacksWithFile(self):
        cacheFolder = 'tests/cacheFolder'
        shutil.rmtree(cacheFolder, ignore_errors=True)

        defaultArgs = ['--cache', cacheFolder, '--source', 'tests/testStacks', '--user', 'dummy:password', '-r', 'tests/testStacks/stackList.txt', '-i', 'tests/testStacks/swarm.management.yml']
        self.assertTrue(os.path.isdir('tests/testStacks'))
        args = ['module', 'prune'] + defaultArgs
        Main.Main(args)

        args = ['module', 'init'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertInfrastructureExists(True)

        args = ['module', 'deploy'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        TestUtilities.AssertStacksExists(['nginx_test_digest'], False)

        args = ['module', 'prune'] + defaultArgs
        Main.Main(args)
        TestUtilities.AssertStacksExists(['nginx_test'], False)
        TestUtilities.AssertStacksExists(['nginx_test_digest'], False)


if __name__ == '__main__':
    unittest.main()