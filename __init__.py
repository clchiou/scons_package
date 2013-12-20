# Copyright (c) 2013 Che-Liang Chiou

from collections import OrderedDict, defaultdict, deque
import os
import re

from SCons.Script import Dir
from SCons.Script import Environment


class RuleRegistry:

    Instance = None

    @classmethod
    def get_instance(cls):
        if cls.Instance is None:
            cls.Instance = cls()
        return cls.Instance

    def __init__(self):
        self.rules = OrderedDict()

    def __iter__(self):
        return iter(self.rules)

    def __getitem__(self, label):
        assert isinstance(label, Label)
        return self.rules[label]

    def add_rule(self, rule):
        assert isinstance(rule, Rule)
        self.rules[rule.label] = rule


class Rule(object):

    def __init__(self, label, input_labels, output_labels, attributes):
        assert isinstance(label, LabelOfRule)
        assert all(isinstance(label, Label) for label in input_labels)
        assert all(isinstance(label, LabelOfFile) for label in output_labels)
        self.label = label
        self.input_labels = input_labels
        self.output_labels = output_labels
        self.attributes = attributes
        self.input_rule_labels = [label for label in self.input_labels
                if isinstance(label, LabelOfRule)]
        self._output = None

    def has_output(self):
        return self._output is not None

    def get_output(self):
        if self._output is None:
            raise RuntimeError('incorrect topology sort')
        return self._output

    def set_output(self, output):
        if self._output is not None:
            raise RuntimeError('incorrect topology sort')
        self._output = output

    output = property(get_output, set_output)

    @staticmethod
    def compute_output_of(label):
        assert isinstance(label, Label)
        if isinstance(label, LabelOfFile):
            return [label.path]
        elif isinstance(label, LabelOfRule):
            rule = RuleRegistry.get_instance()[label]
            return rule.output
        else:
            raise TypeError('unhandled label subtype: %s' % repr(label))


class RuleOfStaticLibrary(Rule):

    @classmethod
    def make(cls, label, input_labels):
        lib_label = LabelOfFile(label.package_name, label.target_name)
        return cls(label, input_labels, [lib_label], {})

    def make_builders(self, env):
        assert isinstance(env, Environment)
        target = self.output_labels[0].path
        source = []
        for input_label in self.input_labels:
            source.extend(self.compute_output_of(input_label))
        self.output = env.StaticLibrary(target=target, source=source)


class RuleOfProgram(Rule):

    @classmethod
    def make(cls, label, input_labels):
        exe_label = LabelOfFile(label.package_name, label.target_name)
        return cls(label, input_labels, [exe_label], {})

    def make_builders(self, env):
        assert isinstance(env, Environment)
        target = self.output_labels[0].path
        source = []
        for input_label in self.input_labels:
            source.extend(self.compute_output_of(input_label))
        self.output = env.Program(target=target, source=source)


class Label(object):

    VALID_NAME = re.compile(r'^[A-Za-z0-9_.\-/]+$')

    @classmethod
    def make_label(cls, label_str):
        package_str = None
        target_str = None
        if not isinstance(label_str, str):
            # Assume it is a File node.
            label_str = label_str.srcnode().path
            package_str, target_str = os.path.split(label_str)
        elif label_str.startswith('#'):
            label_str = label_str[1:]
            if ':' in label_str:
                package_str, target_str = label_str.split(':', 1)
            else:
                package_str = label_str
        elif ':' in label_str:
            package_str, target_str = label_str.split(':', 1)
        else:
            target_str = label_str
        package_name = PackageName(package_str)
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
        return 'Label("%s")' % str(self)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self))

    @property
    def path(self):
        return os.path.join(self.package_name.path, self.target_name.path)


class LabelOfRule(Label):

    def __repr__(self):
        return 'LabelOfRule("%s")' % str(self)


class LabelOfFile(Label):

    def __repr__(self):
        return 'LabelOfFile("%s")' % str(self)


class PackageName:

    def __init__(self, package_name=None):
        # TODO(clchiou): This breaks after SConscriptChdir(0) is called.
        package_name = package_name or Dir('.').srcnode().path
        assert isinstance(package_name, str)
        Label.check_name(package_name)
        self.package_name = package_name

    def __str__(self):
        return self.package_name

    def __repr__(self):
        return 'PackageName("%s")' % self.package_name

    @property
    def path(self):
        return self.package_name


class TargetName:

    def __init__(self, target_name):
        assert isinstance(target_name, str)
        Label.check_name(target_name)
        self.target_name = target_name

    def __str__(self):
        return self.target_name

    def __repr__(self):
        return 'TargetName("%s")' % self.target_name

    @property
    def path(self):
        return self.target_name


def cc_program(name, srcs, deps=()):
    label = LabelOfRule.make_label(name)
    input_labels = LabelOfFile.make_label_list(srcs)
    input_labels.extend(LabelOfRule.make_label_list(deps))
    rule = RuleOfProgram.make(label, input_labels)
    RuleRegistry.get_instance().add_rule(rule)


def cc_library(name, srcs, deps=()):
    label = LabelOfRule.make_label(name)
    input_labels = LabelOfFile.make_label_list(srcs)
    input_labels.extend(LabelOfRule.make_label_list(deps))
    rule = RuleOfStaticLibrary.make(label, input_labels)
    RuleRegistry.get_instance().add_rule(rule)


def make_builders(env):
    assert isinstance(env, Environment)
    rule_reg = RuleRegistry.get_instance()
    rule_queue = deque()
    dep = dict()
    reverse_dep = defaultdict(set)
    for label in rule_reg:
        rule = rule_reg[label]
        if not rule.input_rule_labels:
            rule_queue.append(rule)
        for input_label in rule.input_rule_labels:
            reverse_dep[input_label].add(label)
        dep[label] = set(rule.input_rule_labels)
    while rule_queue:
        rule = rule_queue.popleft()
        rule.make_builders(env)
        for label in reverse_dep[rule.label]:
            dep_labels = dep[label]
            dep_labels.remove(rule.label)
            if not dep_labels:
                rule_queue.append(rule_reg[label])
    if not all(rule_reg[label].has_output() for label in rule_reg):
        raise RuntimeError('incorrect topology sort')
