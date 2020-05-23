from .ignitelogdatamixin import IgniteLogDataMixin


class IgniteCommunicationMixin(IgniteLogDataMixin):
    """
    Provides useful wrappers over Ignite HTTP Communication protocol
    """

    def __init__(self, *args, **kwargs):
        super(IgniteCommunicationMixin, self).__init__(*args, **kwargs)

        self.add_node_data_log_parsing_mask(
            name='Communication',
            node_data_key='communication_port',
            remote_regex='Successfully bound communication NIO server to TCP port',
            local_regex='port=([0-9]+)',
            force_type='int',
        )
