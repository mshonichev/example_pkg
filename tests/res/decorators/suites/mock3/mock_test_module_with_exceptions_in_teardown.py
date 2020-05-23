from tiden.util import with_setup, log_print
from tiden.tidenexception import TidenException


class MockTestWithExceptionsInTeardown:
    def __init__(self, config, ssh_pool):
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    def setup_testcase(self):
        log_print('This is mock setup test case')

    def teardown_testcase(self):
        log_print('This is mock teardown test case')

    @with_setup('setup_testcase', 'teardown_testcase')
    def test_should_pass(self):
        log_print('This is just fake test to test Runner!!!')

    @with_setup(setup_testcase, teardown_testcase)
    def test_should_pass_too(self):
        log_print('This is just another fake test to test Runner!!!')


class MockTestModuleWithTidenExceptionsInTeardown(MockTestWithExceptionsInTeardown):
    def teardown(self):
        raise TidenException('Tiden Exception in module teardown')


class MockTestModuleWithGenericExceptionsInTeardown(MockTestWithExceptionsInTeardown):
    def teardown(self):
        raise Exception('Exception in module teardown')