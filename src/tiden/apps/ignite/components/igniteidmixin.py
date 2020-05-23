from .ignitelogdatamixin import IgniteLogDataMixin


class IgniteIDMixin(IgniteLogDataMixin):
    """
    Provides information about nodeId
    """

    def __init__(self, *args, **kwargs):
        super(IgniteIDMixin, self).__init__(*args, **kwargs)

        self.add_node_data_log_parsing_mask(
            name='id',
            node_data_key='id',
            remote_regex='Local node \[ID=.*, order',
            local_regex='Local node \[ID=(.*), order',
        )
