# Copyright (c) 2013 Che-Liang Chiou

from SCons.Script import Environment

from scons_package.label import LabelOfFile, LabelOfRule
from scons_package.rule import Rule

# Attribute keys
BUILD_OUTPUT = 'build_output'
ENV          = 'env'
EXPORT_ENV   = 'export_env'

DEFAULT_VARIANT = 'host'


class BuilderMakerBuilder:

    BUILDER_TYPES = frozenset('StaticLibrary Program'.split())

    def __init__(self):
        self.builder_type = None
        self.rule = None
        self.variant = DEFAULT_VARIANT
        self.env = None
        self.export_env = None

    def set_builder_type(self, builder_type):
        if builder_type not in self.BUILDER_TYPES:
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
        assert self.builder_type is not None
        assert self.rule is not None
        assert self.variant is not None
        builder_maker = self._build_builder_maker(self.builder_type)
        bmreg.set_builder_maker(self.rule, builder_maker)
        bmreg.set_variant(self.rule, self.variant)
        bmreg.add_rule(self.rule)
        if self.env is not None:
            bmreg.set_attr(self.rule, ENV, self.env)
        if self.export_env is not None:
            bmreg.set_attr(self.rule, EXPORT_ENV, self.export_env)


    @staticmethod
    def _build_builder_maker(builder_type):
        def builder_maker(rule, bmreg):
            # Get target/package/default env (in that order)
            try:
                env = bmreg.get_attr(rule, ENV)
            except KeyError:
                env = bmreg.get_env(rule.name.package_name)
            # Create target and source
            target = rule.outputs[0].path
            source = [label.path for label in rule.inputs]
            for dep in rule.depends:
                output = bmreg.get_attr(dep, BUILD_OUTPUT)
                assert output is not None
                source.extend(output)
            # Import exported environment from depends
            new_env = None
            for dep in rule.depends:
                export_env = bmreg.get_attr(dep, EXPORT_ENV)
                if export_env is None:
                    continue
                if new_env is None:
                    new_env = env.Clone()
                export_env(new_env)  # Modify env in place
            if new_env is not None:
                env = new_env
            # Call builder and make alias
            builder = getattr(env, builder_type)
            output = builder(target=target, source=source)
            bmreg.set_attr(rule, BUILD_OUTPUT, output)
            env.Alias(str(rule.name), output)

        return builder_maker
