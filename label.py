# Copyright (c) 2013 Che-Liang Chiou

import os
import re

from SCons.Script import Dir


class Label(object):

    VALID_NAME = re.compile(r'^[A-Za-z0-9_.\-/]+$')

    @classmethod
    def make_label(cls, label_str):
        package_str = None
        target_str = None
        if not isinstance(label_str, str):
            # Assume it is a SCons File node.
            label_str = label_str.srcnode().path
            package_str, target_str = os.path.split(label_str)
        elif label_str.startswith('#'):
            label_str = label_str[1:]
            if ':' in label_str:
                package_str, target_str = label_str.split(':', 1)
            else:
                package_str = label_str
        elif label_str.startswith(':'):
            target_str = label_str[1:]
        else:
            target_str = label_str
        package_name = PackageName.make_package_name(package_str)
        if not target_str:
            target_str = os.path.basename(package_name.path)
        target_name = TargetName(target_str)
        return cls(package_name, target_name)

    @classmethod
    def make_label_list(cls, label_strs):
        if isinstance(label_strs, str):
            label_strs = label_strs.split()
        return [cls.make_label(label_str) for label_str in label_strs]

    @staticmethod
    def check_name(name):
        if not name:
            raise ValueError('empty name')
        if name.startswith('/') or name.endswith('/'):
            raise ValueError('leading or trailing path separator: %s' % name)
        if '//' in name:
            raise ValueError('consecutive path separators: %s' % name)
        if not Label.VALID_NAME.match(name):
            raise ValueError('invalid name character: %s' % name)

    def __init__(self, package_name, target_name):
        assert isinstance(package_name, PackageName)
        assert isinstance(target_name, TargetName)
        self.package_name = package_name
        self.target_name = target_name

    def __str__(self):
        return '#%s:%s' % (self.package_name, self.target_name)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, str(self))

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.package_name == other.package_name and
                self.target_name == other.target_name)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))

    @property
    def path(self):
        return os.path.join(self.package_name.path, self.target_name.path)


class LabelOfRule(Label):
    pass


class LabelOfFile(Label):
    pass


class PackageName(object):

    @classmethod
    def make_package_name(cls, package_str=None):
        assert package_str is None or isinstance(package_str, str)
        if not package_str:
            package_str = Dir('.').srcnode().path
        return cls(package_str)

    def __init__(self, package_name):
        assert isinstance(package_name, str)
        Label.check_name(package_name)
        self.package_name = package_name

    def __str__(self):
        return self.package_name

    def __repr__(self):
        return 'PackageName("%s")' % self.package_name

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.package_name == other.package_name)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.package_name)

    @property
    def path(self):
        return self.package_name


class TargetName(object):

    def __init__(self, target_name):
        assert isinstance(target_name, str)
        Label.check_name(target_name)
        self.target_name = target_name

    def __str__(self):
        return self.target_name

    def __repr__(self):
        return 'TargetName("%s")' % self.target_name

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.target_name == other.target_name)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.target_name)

    @property
    def path(self):
        return self.target_name
