from .ignitelogdatamixin import IgniteLogDataMixin


class IgniteBinRestMixin(IgniteLogDataMixin):
    """
    Provides access to Snapshot and Control utilities, instantiates on demand.

    Example:

        ignite = Ignite(...)
        ignite.cu.activate()
    """
    _cu = None

    def __init__(self, *args, **kwargs):
        # print('IgniteBinRestMixin.__init__')
        super(IgniteBinRestMixin, self).__init__(*args, **kwargs)

        self.add_node_data_log_parsing_mask(
            name='CommandPort',
            node_data_key='binary_rest_port',
            remote_regex='\[GridTcpRestProtocol\] Command protocol successfully started',
            local_regex='port=([0-9]+)\]',
            force_type='int'
        )
        self.add_node_data_log_parsing_mask(
            name='ClientConnectorPort',
            node_data_key='client_connector_port',
            remote_regex='\[ClientListenerProcessor\] Client connector processor has started on TCP port',
            local_regex='port ([0-9]+)',
            force_type='int'
        )

    def get_control_utility(self):
        if self._cu is None:
            from tiden.utilities.control_utility import ControlUtility
            self._cu = ControlUtility(self)
        return self._cu

    cu = property(get_control_utility, None)
