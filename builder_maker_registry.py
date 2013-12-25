# Copyright (c) 2013 Che-Liang Chiou

from collections import defaultdict
import os
import sys

from SCons.Script import Environment, SConscript

from scons_package.label import Label, PackageName, PackageTrie
from scons_package.rule import Rule, RuleRegistry
from scons_package.utils import topology_sort


BUILDER_MAKER = 'builder_maker'
VARIANT       = 'variant'


class BuilderMakerRegistry:

    RESERVED = frozenset((BUILDER_MAKER, VARIANT))

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
        self.build_order = None

    def get_env(self, package_name):
        assert isinstance(package_name, PackageName)
        assert self.build_order is not None
        return self.envs.search(package_name)

    def set_default_env(self, env):
        assert isinstance(env, Environment)
        assert self.build_order is None
        self.envs.default_env = env

    def set_package_env(self, package_name, env):
        assert isinstance(package_name, PackageName)
        assert isinstance(env, Environment)
        assert self.build_order is None
        self.envs.add_env(package_name, env)

    def add_rule(self, rule):
        assert isinstance(rule, Rule)
        assert self.build_order is None
        if self.rules.has_rule(rule):
            raise RuntimeError('duplicated rule: %s' % rule.name)
        self.rules.add_rule(rule)

    def get_attr(self, label, key):
        assert isinstance(label, (Label, Rule))
        if isinstance(label, Rule):
            label = label.name
        return self.label_attrs.get_attr(label, key)

    def set_attr(self, label, key, value):
        assert isinstance(label, (Label, Rule))
        assert key not in self.RESERVED
        if isinstance(label, Rule):
            label = label.name
        self.label_attrs.set_attr(label, key, value)

    def set_builder_maker(self, label, builder_maker):
        assert isinstance(label, (Label, Rule))
        assert callable(builder_maker)
        assert self.build_order is None
        if isinstance(label, Rule):
            label = label.name
        self.label_attrs.set_attr(label, BUILDER_MAKER, builder_maker)

    def set_variant(self, label, variant):
        assert isinstance(label, (Label, Rule))
        assert isinstance(variant, str)
        assert self.build_order is None
        if isinstance(label, Rule):
            label = label.name
        self.label_attrs.set_attr(label, VARIANT, variant)

    def make_builders(self, sconscript, build_root, variants, duplicate):
        assert self.build_order is None
        self.build_order = BuildOrder.make(self, self.rules, variants)
        for variant in self.build_order.get_variants():
            variant_dir = os.path.join(build_root, variant)
            SConscript(sconscript,
                    variant_dir=variant_dir,
                    duplicate=duplicate,
                    exports={'variant': variant})

    def make_variant_builders(self, variant):
        assert self.build_order is not None
        for rule in self.build_order.get_rules(variant):
            builder_maker = self.label_attrs.get_attr(rule.name, BUILDER_MAKER)
            builder_maker(rule, self)


class BuildOrder:

    @classmethod
    def make(cls, bmreg, rules, variants):
        assert isinstance(bmreg, BuilderMakerRegistry)
        assert isinstance(rules, RuleRegistry)
        cls._check_depends(rules)
        for label in rules:
            cls._check_same_variants(bmreg, rules[label])

        graph = defaultdict(set)
        for label_from in rules:
            variant_from = bmreg.get_attr(label_from, VARIANT)
            for label_to in rules[label_from].depends:
                variant_to = bmreg.get_attr(label_to, VARIANT)
                if variant_from != variant_to:
                    graph[variant_from].add(variant_to)
        def get_neighbors(variant):
            return graph[variant]
        variants = topology_sort(variants, get_neighbors)

        variant_rules = defaultdict(list)
        for rule in rules.get_sorted_rules():
            variant_rules[bmreg.get_attr(rule, VARIANT)].append(rule)

        assert len(variants) == len(variant_rules)
        return cls(variants, variant_rules)

    @staticmethod
    def _check_depends(rules):
        okay = True
        for name, depend in rules.get_missing_dependencies():
            sys.stderr.write('%s depends on non-existing %s\n' % (name, depend))
            sys.stderr.write('Targets in package %s:\n' % depend.package_name)
            for label in rules:
                if label.package_name == depend.package_name:
                    sys.stderr.write('    %s\n' % label)
            sys.stderr.write('\n')
            okay = False
        if not okay:
            raise RuntimeError('missing dependencies')

    @staticmethod
    def _check_same_variants(bmreg, rule):
        variant_rule = bmreg.get_attr(rule, VARIANT)
        for label in rule.depends:
            variant = bmreg.get_attr(label, VARIANT)
            if variant_rule != variant:
                raise RuntimeError('variant of %s and %s differ: %s, %s' %
                        (rule.name, label, variant_rule, variant))

    def __init__(self, variants, variant_rules):
        self.variants = variants
        self.variant_rules = variant_rules

    def get_variants(self):
        return self.variants

    def get_rules(self, variant):
        return self.variant_rules[variant]


class LabelAttributes:

    def __init__(self):
        self.attributes = defaultdict(dict)

    def get_attr(self, label, key):
        assert isinstance(label, Label)
        assert isinstance(key, str)
        return self.attributes[label][key]

    def set_attr(self, label, key, value):
        assert isinstance(label, Label)
        assert isinstance(key, str)
        self.attributes[label][key] = value


class EnvironmentRegistry(object):

    def __init__(self):
        self.package_trie = PackageTrie()
        self.envs = {}
        self._default_env = None

    def get_default_env(self):
        return self._default_env

    def set_default_env(self, env):
        assert isinstance(env, Environment)
        self._default_env = env

    default_env = property(get_default_env, set_default_env)

    def add_env(self, package_name, env):
        assert isinstance(package_name, PackageName)
        assert isinstance(env, Environment)
        if package_name in self.envs:
            raise KeyError('overwrite package: %s' % package_name)
        self.package_trie.add(package_name)
        self.envs[package_name] = env

    def search(self, package_name):
        assert isinstance(package_name, PackageName)
        package_name = self.package_trie.search(package_name)
        if package_name is None:
            if self._default_env is None:
                raise KeyError(str(package_name))
            return self._default_env
        return self.envs[package_name]
