# Copyright (c) 2013 Che-Liang Chiou

from collections import OrderedDict

from scons_package.label import Label, LabelOfRule, LabelOfFile
from scons_package.utils import topology_sort


class RuleRegistry:

    def __init__(self):
        self.rules = OrderedDict()

    def __len__(self):
        return len(self.rules)

    def __iter__(self):
        return iter(self.rules)

    def __getitem__(self, label):
        assert isinstance(label, Label)
        return self.rules[label]

    def has_rule(self, rule):
        return rule.name in self.rules

    def add_rule(self, rule):
        assert isinstance(rule, Rule)
        self.rules[rule.name] = rule

    def get_missing_dependencies(self):
        for label, rule in self.rules.items():
            for depend in rule.depends:
                if depend not in self.rules:
                    yield label, depend

    def get_sorted_rules(self):
        def get_neighbors(rule):
            assert isinstance(rule, Rule)
            return (self.rules[label] for label in rule.depends)
        return topology_sort(self.rules.values(), get_neighbors)


class Rule(object):

    def __init__(self, name, inputs, depends, outputs):
        assert isinstance(name, LabelOfRule)
        assert all(isinstance(label, LabelOfFile) for label in inputs)
        assert all(isinstance(label, LabelOfRule) for label in depends)
        assert all(isinstance(label, LabelOfFile) for label in outputs)
        for label in inputs:
            if name.package_name != label.package_name:
                raise ValueError('input outside the package: %s, %s' %
                                 (repr(label), repr(name)))
        for label in outputs:
            if name.package_name != label.package_name:
                raise ValueError('output outside the package: %s, %s' %
                                 (repr(label), repr(name)))
        if name in inputs or name in depends:
            raise ValueError('rule depends on itself: %s' % name)
        self.name = name
        self.inputs = inputs
        self.depends = depends
        self.outputs = outputs
