# Copyright (c) 2013 Che-Liang Chiou

from SCons.Script import Environment

from scons_package.builder_maker_builder import BuilderMakerBuilder
from scons_package.builder_maker_registry import BuilderMakerRegistry
from scons_package.label import PackageName
from scons_package.utils import glob

__all__ = ['cc_library',
           'cc_program',
           'glob',
           'make_builders',
           'register_env',
           'register_root_env']


def register_root_env(env):
    assert isinstance(env, Environment)
    BuilderMakerRegistry.get_instance().set_root_env(env)


def register_env(env, package_str=None):
    assert isinstance(env, Environment)
    assert package_str is None or isinstance(package_str, str)
    package_name = PackageName.make_package_name(package_str)
    BuilderMakerRegistry.get_instance().set_env(package_name, env)


def cc_program(name, srcs, deps=()):
    bmb = BuilderMakerBuilder()
    bmb.set_builder_type('Program')
    bmb.set_name_srcs_deps(name, srcs, deps)
    bmb.build(BuilderMakerRegistry.get_instance())


def cc_library(name, srcs, deps=(), export_env=None):
    assert export_env is None or callable(export_env)
    bmb = BuilderMakerBuilder()
    bmb.set_builder_type('StaticLibrary')
    bmb.set_name_srcs_deps(name, srcs, deps)
    if export_env is not None:
        bmb.set_export_env(export_env)
    bmb.build(BuilderMakerRegistry.get_instance())


def make_builders():
    BuilderMakerRegistry.get_instance().make_builders()
