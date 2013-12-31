# Copyright (c) 2013 Che-Liang Chiou

from collections import defaultdict

from scons_package.label import Label
from scons_package.rule import Rule, RuleRegistry


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

    def add_rule(self, rule):
        assert isinstance(rule, Rule)
        # Not thread-safe...
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
        if isinstance(label, Rule):
            label = label.name
        self.label_attrs.set_attr(label, key, value)


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
