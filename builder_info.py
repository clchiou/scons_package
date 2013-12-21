# Copyright (c) 2013 Che-Liang Chiou

from collections import defaultdict

from SCons.Script import Environment

from scons_package.label import Label, PackageName, PackageTrie
from scons_package.rule import RuleRegistry, Rule, topology_sort


BUILDER_MAKER = 'builder-maker'
BUILD_OUTPUT = 'build-output'


class BuilderContext:

    Instance = None

    @classmethod
    def get_instance(cls):
        if cls.Instance is None:
            cls.Instance = cls()
        return cls.Instance

    def __init__(self):
        self.rules = RuleRegistry()
        self.rule_attrs = RuleAttributes()
        self.envs = EnvironmentRegistry()


class RuleAttributes:

    def __init__(self):
        self.attributes = defaultdict(dict)

    def get_attr(self, label, key):
        assert isinstance(label, Label)
        return self.attributes[label].get(key)

    def set_attr(self, label, key, value):
        assert isinstance(label, Label)
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


def register_rule(context, rule, maker):
    assert isinstance(rule, Rule)
    context.rules.add_rule(rule)
    context.rule_attrs.set_attr(rule.name, BUILDER_MAKER, maker)


def make_builders(context):
    sorted_rules = topology_sort(context.rules)
    for rule in sorted_rules:
        env = context.envs.search(rule.name.package_name)
        builder_maker = context.rule_attrs.get_attr(rule.name, BUILDER_MAKER)
        builder_maker(context, rule, env)
