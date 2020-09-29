# from .models import Msg


class DotDict(dict):
    """dot.notation access to dictionary attributes"""

    def __getattr__(self, attr):
        return self.get(attr)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self


MESSAGE_TYPE = DotDict(dict(
    OUTGOING="Outgoing",
    INCOMING="Incoming"
))


def logMsg(msg):
    pass
