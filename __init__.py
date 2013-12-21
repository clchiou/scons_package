# Copyright (c) 2013 Che-Liang Chiou

from SCons.Script import Environment

from scons_package.builder_info import BuilderContext
from scons_package.label import LabelOfFile, LabelOfRule, PackageName
from scons_package.rule import Rule, RuleRegistry

import scons_package.builder_info as builder_info


__all__ = ['register_root_env',
           'register_env',
           'cc_program',
           'cc_library',
           'make_builders']


def register_root_env(env):
    assert isinstance(env, Environment)
    context = BuilderContext.get_instance()
    context.envs.root_env = env


def register_env(env, package_str=None):
    assert isinstance(env, Environment)
    assert package_str is None or isinstance(package_str, str)
    context = BuilderContext.get_instance()
    package_name = PackageName.make_package_name(package_str)
    context.envs.add_env(package_name, env)


def cc_program(name, srcs, deps=()):
    def maker(context, rule, env):
        target = rule.outputs[0].path
        source = [label.path for label in rule.inputs]
        for dep in rule.depends:
            outs = context.rule_attrs.get_attr(dep, builder_info.BUILD_OUTPUT)
            source.extend(outs)
        outs = env.Program(target=target, source=source)
        context.rule_attrs.set_attr(rule.name, builder_info.BUILD_OUTPUT, outs)

    outputs = [LabelOfFile.make_label(name)]
    cc_base(name, srcs, deps, outputs, maker)


def cc_library(name, srcs, deps=()):
    def maker(context, rule, env):
        target = rule.outputs[0].path
        source = [label.path for label in rule.inputs]
        for dep in rule.depends:
            outs = context.rule_attrs.get_attr(dep, builder_info.BUILD_OUTPUT)
            source.extend(outs)
        outs = env.StaticLibrary(target=target, source=source)
        context.rule_attrs.set_attr(rule.name, builder_info.BUILD_OUTPUT, outs)

    outputs = [LabelOfFile.make_label(name)]
    cc_base(name, srcs, deps, outputs, maker)


def cc_base(name, srcs, deps, outputs, maker):
    context = BuilderContext.get_instance()
    name = LabelOfRule.make_label(name)
    inputs = LabelOfFile.make_label_list(srcs)
    depends = LabelOfRule.make_label_list(deps)
    rule = Rule(name, inputs, depends, outputs)
    builder_info.register_rule(context, rule, maker)


def make_builders():
    context = BuilderContext.get_instance()
    builder_info.make_builders(context)
