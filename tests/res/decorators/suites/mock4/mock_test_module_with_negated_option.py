
from tiden.configuration_decorator import test_configuration
from tiden.util import require
from tiden.testconfig import test_config
from time import sleep

class MockTestModuleWithNegatedOption:
    """
    Example test class with few boolean configuration options checked via `@require`.
    Options are detected as boolean when their name ends with '_enabled'.
    """
    def __init__(self, config, ssh_pool):
        pass

    def test_main(self):
        pass

    @require(~test_config.zookeeper_enabled)
    def test_without_zookeeper_only(self):
        pass

    @require(test_config.zookeeper_enabled)
    def test_with_zookeeper_only(self):
        pass

    def teardown(self):
        pass
