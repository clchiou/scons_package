# Copyright (c) 2013 Che-Liang Chiou

from collections import defaultdict
import sys

from SCons.Script import Environment

from scons_package.label import Label, PackageName, PackageTrie
from scons_package.rule import Rule, RuleRegistry, check_depends, topology_sort


BUILDER_MAKER = 'builder_maker'


class BuilderMakerRegistry:

    Instance = None

    @classmethod
    def get_instance(cls):
        if cls.Instance is None:
            cls.Instance = cls()
        return cls.Instance

    def __init__(self):
        self.rules = RuleRegistry()
        self.label_attrs = LabelAttributes()
        self.envs = EnvironmentRegistry()

    def set_root_env(self, env):
        assert isinstance(env, Environment)
        self.envs.root_env = env

    def set_env(self, package_name, env):
        assert isinstance(package_name, PackageName)
        assert isinstance(env, Environment)
        self.envs.add_env(package_name, env)

    def set_attr(self, label, key, value):
        assert isinstance(label, (Label, Rule))
        assert key != BUILDER_MAKER  # BUILDER_MAKER is reserved.
        if isinstance(label, Rule):
            rule = label
            if not self.rules.has_rule(rule):
                self.rules.add_rule(rule)
            label = rule.name
        self.label_attrs.set_attr(label, key, value)

    def get_attr(self, label, key):
        assert isinstance(label, (Label, Rule))
        if isinstance(label, Rule):
            rule = label
            label = rule.name
        return self.label_attrs.get_attr(label, key)

    def set_builder_maker(self, label, builder_maker):
        assert isinstance(label, (Label, Rule))
        assert callable(builder_maker)
        if isinstance(label, Rule):
            rule = label
            if not self.rules.has_rule(rule):
                self.rules.add_rule(rule)
            label = rule.name
        self.label_attrs.set_attr(label, BUILDER_MAKER, builder_maker)

    def check_depends(self):
        okay = True
        for name, depend in check_depends(self.rules):
            sys.stderr.write('%s depends on non-existing %s\n' % (name, depend))
            sys.stderr.write('Targets in package %s:\n' % depend.package_name)
            for label in self.rules:
                if label.package_name == depend.package_name:
                    sys.stderr.write('    %s\n' % label)
            sys.stderr.write('\n')
            okay = False
        if not okay:
            raise RuntimeError('missing dependencies')

    def make_builders(self):
        self.check_depends()
        sorted_rules = topology_sort(self.rules)
        for rule in sorted_rules:
            env = self.envs.search(rule.name.package_name)
            builder_maker = self.label_attrs.get_attr(rule.name, BUILDER_MAKER)
            builder_maker(rule, env, self)


class LabelAttributes:

    def __init__(self):
        self.attributes = defaultdict(dict)

    def get_attr(self, label, key):
        assert isinstance(label, Label)
        assert isinstance(key, str)
        return self.attributes[label].get(key)

    def set_attr(self, label, key, value):
        assert isinstance(label, Label)
        assert isinstance(key, str)
        self.attributes[label][key] = value


class EnvironmentRegistry(object):

    def __init__(self):
        self.package_trie = PackageTrie()
        self.envs = {}
        self._root_env = Environment()

    def get_root_env(self):
        return self._root_env

    def set_root_env(self, env):
        assert isinstance(env, Environment)
        self._root_env = env

    root_env = property(get_root_env, set_root_env)

    def add_env(self, package_name, env):
        assert isinstance(package_name, PackageName)
        assert isinstance(env, Environment)
        if package_name in self.envs:
            raise KeyError('overwrite package: %s' % package_name)
        self.package_trie.add(package_name)
        self.envs[package_name] = env

    def search(self, package_name):
        assert isinstance(package_name, PackageName)
        try:
            package_name = self.package_trie.search(package_name)
        except KeyError:
            return self._root_env
        return self.envs[package_name]
