# Copyright (c) 2013 Che-Liang Chiou

from scons_package.builder_maker_registry import BuilderMakerRegistry
from scons_package.package_registry import PackageEnvironmentRegistry

# Attributes
BUILD_OUTPUT = 'build_output'
BUILDER_TYPE = 'builder_type'
ENV = 'env'
EXPORT_ENV = 'export_env'
VARIANT = 'variant'

# Builder types
PROGRAM = 'Program'
STATIC_LIBRARY = 'StaticLibrary'
BUILDER_TYPES = frozenset((PROGRAM, STATIC_LIBRARY))


def builder_maker(rule, bmreg, pereg):
    '''Make SCons builder of a given rule.'''
    assert isinstance(bmreg, BuilderMakerRegistry)
    assert isinstance(pereg, PackageEnvironmentRegistry)
    # Retrieve environment from rule/package/default (in that order)
    try:
        env = bmreg.get_attr(rule, ENV)
    except KeyError:
        env = pereg.search(rule.name.package_name)
    # Create target and source
    assert len(rule.outputs) == 1
    target = rule.outputs[0].path
    source = [label.path for label in rule.inputs]
    for dep in rule.depends:
        source.extend(bmreg.get_attr(dep, BUILD_OUTPUT))
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
    builder_type = bmreg.get_attr(rule, BUILDER_TYPE)
    builder = getattr(env, builder_type)
    output = builder(target=target, source=source)
    bmreg.set_attr(rule, BUILD_OUTPUT, output)
    env.Alias(str(rule.name), output)
