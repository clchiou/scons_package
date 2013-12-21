# Copyright (c) 2013 Che-Liang Chiou

from collections import OrderedDict, defaultdict, deque

from scons_package.label import Label, LabelOfRule, LabelOfFile


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

    def add_rule(self, rule):
        assert isinstance(rule, Rule)
        self.rules[rule.name] = rule


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

        self.name = name
        self.inputs = inputs
        self.depends = depends
        self.outputs = outputs


def topology_sort(rules):
    assert isinstance(rules, RuleRegistry)
    output = []

    graph = {}
    reverse_graph = defaultdict(list)
    ready = deque()
    for label in rules:
        rule = rules[label]
        graph[label] = set(rule.depends)
        for depend in rule.depends:
            reverse_graph[depend].append(label)
        if not rule.depends:
            ready.append(label)

    while ready:
        label = ready.popleft()
        output.append(rules[label])
        for rdep in reverse_graph[label]:
            deps = graph[rdep]
            deps.remove(label)
            if not deps:
                ready.append(rdep)
    if len(output) != len(rules):
        raise RuntimeError('incorrect topology')

    return output
