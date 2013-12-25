'''Mocked objects.'''


class Dir(object):

    path = 'a/b/c'

    def __init__(self, *args):
        pass

    def srcnode(self):
        return Dir()


class Environment(object):
    pass


class SConscript(object):
    pass
