# Copyright (c) 2013 Che-Liang Chiou

from SCons.Script import Environment

from scons_package import builder_maker
from scons_package.label import LabelOfFile, LabelOfRule
from scons_package.rule import Rule


class BuilderMakerBuilder:

    def __init__(self):
        self.rule = None
        self.builder_type = None
        self.variant = None
        self.env = None
        self.export_env = None

    def set_builder_type(self, builder_type):
        if builder_type not in builder_maker.BUILDER_TYPES:
            raise RuntimeError('unsupported builder type: %s' % builder_type)
        self.builder_type = builder_type

    def set_name_srcs_deps(self, name, srcs, deps):
        label = LabelOfRule.make_label(name)
        inputs = LabelOfFile.make_label_list(srcs)
        depends = LabelOfRule.make_label_list(deps)
        outputs = [LabelOfFile.make_label(name)]
        self.rule = Rule(label, inputs, depends, outputs)

    def set_variant(self, variant):
        assert isinstance(variant, str)
        self.variant = variant

    def set_env(self, env):
        assert isinstance(env, Environment)
        self.env = env

    def set_export_env(self, export_env):
        assert callable(export_env)
        self.export_env = export_env

    def build(self, bmreg):
        assert self.rule is not None
        assert self.builder_type is not None
        bmreg.add_rule(self.rule)
        bmreg.set_attr(self.rule, builder_maker.BUILDER_TYPE,
                       self.builder_type)
        if self.variant is not None:
            bmreg.set_attr(self.rule, builder_maker.VARIANT, self.variant)
        if self.env is not None:
            bmreg.set_attr(self.rule, builder_maker.ENV, self.env)
        if self.export_env is not None:
            bmreg.set_attr(self.rule, builder_maker.EXPORT_ENV,
                           self.export_env)
