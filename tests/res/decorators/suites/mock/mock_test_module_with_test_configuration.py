
from tiden.configuration_decorator import test_configuration
from tiden.util import require
from tiden.testconfig import test_config
from time import sleep

@test_configuration([
    'pitr_enabled',
    'compaction_enabled',
    'zookeeper_enabled'
])
class MockTestModuleWithTestConfiguration:
    """
    Example test class with few boolean configuration options. Options are detected as boolean when their name ends with
    '_enabled'. Test module would have set of configurations equal to direct product of each configuration options
    possible values, which are [True, False]
    """
    def __init__(self, config, ssh_pool):
        pass

    def setup(self):
        pass

    def test_main(self):
        sleep(0.3)

    @require(test_config.zookeeper_enabled)
    def test_zookeeper_only(self):
        pass

    def teardown(self):
        pass
