from .ignitelogdatamixin import IgniteLogDataMixin


class IgniteJmxMixin(IgniteLogDataMixin):
    """
    Provides access to Jmx utility on demand.

    Example usage:

        ignite = Ignite(...)
        ignite.jmx.get_attributes()

    """

    _jmx = None

    def __init__(self, *args, **kwargs):
        # print('IgniteJmxMixin.__init__')
        super(IgniteJmxMixin, self).__init__(*args, **kwargs)

        self.add_node_data_log_parsing_mask(
            name='JMX',
            node_data_key='jmx_port',
            remote_regex='JMX (remote: on, port: [0-9]\+,',
            local_regex='JMX \(remote: on, port: (\d+),',
            force_type='int',
        )

    def get_jmx_utility(self):
        if self._jmx is None:
            from tiden.utilities import JmxUtility
            self._jmx = JmxUtility(self)
        return self._jmx

    jmx = property(get_jmx_utility, None)
