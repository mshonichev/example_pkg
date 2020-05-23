from ...app import App
from ....logger import get_logger


class IgniteMixin(App):
    logger = None

    def __init__(self, *args, **kwargs):
        # print('IgniteMixin.__init__')
        super().__init__(*args, **kwargs)

        self.logger = get_logger('tiden')
