import unittest
from DockerFeed.Handlers.ModuleHandler import ModuleHandler
from tests import TestUtilities

class TestModuleHandler(unittest.TestCase):

    def test_DeployRemove(self):
        handler: ModuleHandler = TestUtilities.CreateModuleHandler()
        handler.Init()
        TestUtilities.AssertInfrastructureExists(True)
        handler.Deploy(['nginx_test'])
        TestUtilities.AssertStacksExists(["nginx_test"], True)
        handler.Remove(['nginx_test'])
        TestUtilities.AssertStacksExists(["nginx_test"], False)

        handler.Deploy(['nginx_test>=1.1.0'])
        TestUtilities.AssertStacksExists(["nginx_test"], True)
        handler.Remove(['nginx_test'])
        TestUtilities.AssertStacksExists(["nginx_test"], False)

        self.assertRaises(Exception, handler.Deploy, ['nginx_test>=2.1.0'])
        self.assertRaises(Exception, handler.Deploy, ['non_existent_nginx_test>=2.1.0'])

    def test_DeployOnlyValidStacks(self):
        handler: ModuleHandler = TestUtilities.CreateModuleHandler(source="tests/invalidTestStacks", verifyStacksOnDeploy=True)
        handler.Init()
        TestUtilities.AssertInfrastructureExists(True)
        handler.Deploy(['nginx_test_invalid'])
        TestUtilities.AssertStacksExists(["nginx_test_invalid_config"], False)
        TestUtilities.AssertStacksExists(["nginx_test_invalid_secret"], False)
        TestUtilities.AssertStacksExists(["nginx_test_invalid_volume"], False)
        TestUtilities.AssertStacksExists(["nginx_test_invalid_port"], False)

    def test_InitPrune(self):
        handler: ModuleHandler = TestUtilities.CreateModuleHandler()
        handler.Init()
        TestUtilities.AssertInfrastructureExists(True)
        handler.Deploy()
        TestUtilities.AssertStacksExists(['nginx_test'], True)
        handler.Prune()
        TestUtilities.AssertStacksExists(['nginx_test'], False)
        stacks = handler.List()
        self.assertGreater(len(stacks), 0)
        TestUtilities.AssertStacksExists(stacks, False)

    def test_List(self):
        handler: ModuleHandler = TestUtilities.CreateModuleHandler()
        stacks = handler.List()
        self.assertFalse('nginx_test==1.0.0' in stacks)
        self.assertTrue('nginx_test==1.1.1' in stacks)

        stacks = handler.List(['nginx_test>1.0.0'])
        self.assertFalse('nginx_test==1.0.0' in stacks)
        self.assertTrue('nginx_test==1.1.1' in stacks)

    def test_Verify(self):
        handler: ModuleHandler = TestUtilities.CreateModuleHandler()
        self.assertFalse(handler.Verify())
        self.assertTrue(handler.Verify(['nginx_test_digest']))



if __name__ == '__main__':
    unittest.main()