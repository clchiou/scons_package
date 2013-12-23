# Copyright (c) 2013 Che-Liang Chiou

from SCons.Script import Environment

from scons_package.builder_maker_builder import BuilderMakerBuilder
from scons_package.builder_maker_registry import BuilderMakerRegistry
from scons_package.label import PackageName
from scons_package.utils import glob

__all__ = ['default_environment',
           'package_environment',
           'library',
           'program',
           'make_builders',
           'make_variant_builders',
           'glob']


def default_environment(env):
    assert isinstance(env, Environment)
    BuilderMakerRegistry.get_instance().set_default_env(env)


def package_environment(env, package_str=None):
    assert isinstance(env, Environment)
    assert package_str is None or isinstance(package_str, str)
    package_name = PackageName.make_package_name(package_str)
    BuilderMakerRegistry.get_instance().set_package_env(package_name, env)


def program(name, srcs, deps=(), variant=None, env=None):
    assert variant is None or isinstance(variant, str)
    assert env is None or isinstance(env, Environment)
    bmb = BuilderMakerBuilder()
    bmb.set_builder_type('Program')
    bmb.set_name_srcs_deps(name, srcs, deps)
    if variant is not None:
        bmb.set_variant(variant)
    if env is not None:
        bmb.set_env(env)
    bmb.build(BuilderMakerRegistry.get_instance())


def library(name, srcs, deps=(), variant=None, env=None, export_env=None):
    assert variant is None or isinstance(variant, str)
    assert env is None or isinstance(env, Environment)
    assert export_env is None or callable(export_env)
    bmb = BuilderMakerBuilder()
    bmb.set_builder_type('StaticLibrary')
    bmb.set_name_srcs_deps(name, srcs, deps)
    if variant is not None:
        bmb.set_variant(variant)
    if env is not None:
        bmb.set_env(env)
    if export_env is not None:
        bmb.set_export_env(export_env)
    bmb.build(BuilderMakerRegistry.get_instance())


def make_builders(sconscript, build_root, variants, duplicate=1):
    bmreg = BuilderMakerRegistry.get_instance()
    bmreg.make_builders(sconscript, build_root, variants, duplicate)


def make_variant_builders(variant):
    BuilderMakerRegistry.get_instance().make_variant_builders(variant)
