from tiden.util import with_setup, log_print
from tiden.tidenexception import TidenException


class MockTestModuleWithExceptionsInSetup:
    def __init__(self, config, ssh_pool):
        pass

    def setup(self):
        raise TidenException('Exception in module setup')

    def teardown(self):
        pass

    def setup_testcase(self):
        log_print('This is mock setup test case')

    def teardown_testcase(self):
        log_print('This is mock teardown test case')

    @with_setup('setup_testcase', 'teardown_testcase')
    def test_should_pass(self):
        log_print('This is just fake test to test Runner!!!')


class MockTestModuleWithGeneralExceptionsInSetup(MockTestModuleWithExceptionsInSetup):
    def setup(self):
        raise Exception('Just General Exception')
