from .generators import gen_permutations

def test_configuration(*args):
    def test_configuration_decorator(cls):
        assert len(args) > 0
        if len(args) >= 1:
            configuration_options = args[0]
        if len(args) >= 2:
            configurations = args[1]
        else:
            configurations = list(
                gen_permutations([
                    [True, False]
                    for configuration_option
                    in configuration_options
                    if configuration_option.endswith('_enabled')
                ])
            )
        cls.__configuration_options__ = configuration_options.copy()
        cls.__configurations__ = configurations.copy()
        return cls
    return test_configuration_decorator
