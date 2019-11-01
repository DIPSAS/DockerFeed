import unittest
import os
from DockerBuildSystem import DockerComposeTools
from DockerFeed.StackHandler import StackHandler
from tests import TestUtilities

class TestStackHandler(unittest.TestCase):

    def test_DeployRemove(self):
        handler: StackHandler = TestUtilities.CreateStackHandler()
        handler.Init()
        TestUtilities.AssertInfrastructureExists(True)
        handler.Deploy(['nginx_test'], verifyStacksOnDeploy=False)
        TestUtilities.AssertStacksExists(["nginx_test"], True)
        handler.Remove(['nginx_test'])
        TestUtilities.AssertStacksExists(["nginx_test"], False)

    def test_DeployOnlyValidStacks(self):
        handler: StackHandler = TestUtilities.CreateStackHandler(stacksFolder="tests/invalidTestStacks")
        handler.Init()
        TestUtilities.AssertInfrastructureExists(True)
        handler.Deploy(['nginx_test_invalid_config'], verifyStacksOnDeploy=True)
        TestUtilities.AssertStacksExists(["nginx_test_invalid_config"], False)
        handler.Deploy(['nginx_test_invalid_secret'], verifyStacksOnDeploy=True)
        TestUtilities.AssertStacksExists(["nginx_test_invalid_secret"], False)
        handler.Deploy(['nginx_test_invalid_volume'], verifyStacksOnDeploy=True)
        TestUtilities.AssertStacksExists(["nginx_test_invalid_volume"], False)
        handler.Deploy(['nginx_test_invalid_port'], verifyStacksOnDeploy=True)
        TestUtilities.AssertStacksExists(["nginx_test_invalid_port"], False)

    def test_InitPrune(self):
        handler: StackHandler = TestUtilities.CreateStackHandler()
        handler.Init()
        TestUtilities.AssertInfrastructureExists(True)
        handler.Deploy(verifyStacksOnDeploy=False)
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        handler.Prune()
        TestUtilities.AssertStacksExists(['nginx_test'], False)
        stacks = handler.List()
        self.assertGreater(len(stacks), 0)
        TestUtilities.AssertStacksExists(stacks, False)

    def test_List_offline(self):
        handler: StackHandler = TestUtilities.CreateStackHandler(offline=True)
        stacks = handler.List()
        self.assertTrue('nginx_test' in stacks)

    def test_List_online(self):
        handler: StackHandler = TestUtilities.CreateStackHandler(offline=False)
        stacks = handler.List()
        self.assertTrue('nginx_test_online' in stacks)

    def test_Verify(self):
        handler: StackHandler = TestUtilities.CreateStackHandler()
        self.assertFalse(handler.Verify())
        self.assertTrue(handler.Verify(['ngint_test_digest']))

    def test_Run(self):
        DockerComposeTools.DockerComposeBuild(["tests/testBatchStacks/docker-compose.batch.yml"])
        handler: StackHandler = TestUtilities.CreateStackHandler(stacksFolder="tests/testBatchStacks",
                                                                 swmInfrastructureFiles=["tests/testBatchStacks/swarm.management,yml"])
        handler.Init()
        os.environ['SHOULD_FAIL'] = 'false'
        self.assertTrue(handler.Run())

        os.environ['SHOULD_FAIL'] = 'true'
        self.assertFalse(handler.Run(['batch']))



if __name__ == '__main__':
    unittest.main()