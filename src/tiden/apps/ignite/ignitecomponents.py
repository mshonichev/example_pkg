
from .components import *

class IgniteComponents(
    IgniteControlThreadMixin,
    IgniteBinRestMixin,
    IgniteJmxMixin,
    IgniteRESTMixin,
    IgniteCommunicationMixin,
    IgniteIDMixin,
    IgniteLibsMixin,
    IgniteStaticInitMixin,
    IgniteTopologyMixin,
    IgniteLogDataMixin,
    IgniteNodesMixin,
):
    def __init__(self, *args, **kwargs):
        # print('IgniteComponents.__init__')
        super(IgniteComponents, self).__init__(*args, **kwargs)

    def do_callback(self, callback_name, *args, **kwargs):
        """
        Invoke callback from all mixins that have it.
        :param callback_name:
        :param args:
        :param kwargs:
        :return:
        """
        cc = []
        cl = self.__class__.__mro__ if kwargs.get('reversed', False) else reversed(self.__class__.__mro__)
        for c in cl:
            if hasattr(c, callback_name):
                m = getattr(c, callback_name)
                if m not in cc:
                    m(self, *args, **kwargs)
                    cc.append(m)
