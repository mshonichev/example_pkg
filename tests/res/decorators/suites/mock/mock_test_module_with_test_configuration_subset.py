
from tiden.configuration_decorator import test_configuration

@test_configuration([
    'pitr_enabled',
    'compaction_enabled',
    'zookeeper_enabled',
    'load_factor',
], [
    [True, True, True, 0.1],
    [True, False, True, 1.0],
    [True, True, False, 0.1],
    [True, False, False, 1.0],
])
class MockTestModuleWithTestConfigurationSubset:
    """
    Example test class with limited set of configurations
    """
    def __init__(self, config, ssh_pool):
        pass

    def setup(self):
        pass

    def test_whatever_more(self):
        pass

    def teardown(self):
        pass
