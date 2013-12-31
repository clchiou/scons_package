# Copyright (c) 2013 Che-Liang Chiou

'''Public API of scons_package.'''

from SCons.Script import Dir, Environment

from scons_package import builder_maker
from scons_package.builder_maker_builder import BuilderMakerBuilder
from scons_package.builder_maker_registry import BuilderMakerRegistry
from scons_package.exec_build_makers import BuilderMakerOrder
from scons_package.exec_build_makers import exec_builder_makers
from scons_package.exec_build_makers import exec_variant_builder_makers
from scons_package.label import PackageName
from scons_package.package_registry import PackageVariantRegistry
from scons_package.package_registry import PackageEnvironmentRegistry
from scons_package.utils import glob

__all__ = ['search_package_environment',
           'search_package_variant',
           'package_environment',
           'package_variant',
           'library',
           'program',
           'make_builders',
           'make_variant_builders',
           'glob']


def search_package_environment(package=None):
    '''Search package's environment.'''
    assert package is None or isinstance(package, str)
    return _package_get(PackageEnvironmentRegistry.get_instance(), package)


def search_package_variant(package=None):
    '''Search package's variant.'''
    assert package is None or isinstance(package, str)
    return _package_get(PackageVariantRegistry.get_instance(), package)


def package_environment(env, package=None):
    '''Set package's environment.'''
    assert isinstance(env, Environment)
    assert package is None or isinstance(package, str)
    _package_set(PackageEnvironmentRegistry.get_instance(), package, env)


def package_variant(variant, package=None):
    '''Set package's variant.'''
    assert isinstance(variant, str)
    assert package is None or isinstance(package, str)
    _package_set(PackageVariantRegistry.get_instance(), package, variant)


def _package_get(trie, package_str):
    pkg_name = PackageName.make_package_name(package_str)
    return trie.search(pkg_name)


def _package_set(trie, package_str, value):
    if package_str is None and Dir('.') == Dir('#'):
        trie.default = value
    else:
        pkg_name = PackageName.make_package_name(package_str)
        trie.add(pkg_name, value)


def program(name, srcs, deps=(), variant=None, env=None):
    '''Declare a program.'''
    assert variant is None or isinstance(variant, str)
    assert env is None or isinstance(env, Environment)
    _builder_maker_builder(builder_maker.PROGRAM,
                           name, srcs, deps, variant, env, None)


def library(name, srcs, deps=(), variant=None, env=None, export_env=None):
    '''Declare a library.'''
    assert variant is None or isinstance(variant, str)
    assert env is None or isinstance(env, Environment)
    assert export_env is None or callable(export_env)
    _builder_maker_builder(builder_maker.STATIC_LIBRARY,
                           name, srcs, deps, variant, env, export_env)


def _builder_maker_builder(builder_type,
                           name, srcs, deps, variant, env, export_env):
    bmb = BuilderMakerBuilder()
    bmb.set_builder_type(builder_type)
    bmb.set_name_srcs_deps(name, srcs, deps)
    if variant is not None:
        bmb.set_variant(variant)
    if env is not None:
        bmb.set_env(env)
    if export_env is not None:
        bmb.set_export_env(export_env)
    bmb.build(BuilderMakerRegistry.get_instance())


def make_builders(sconscript=None, build_root=None, variants=(), duplicate=1):
    '''Generate SCons builders for all variants.'''
    exec_builder_makers(BuilderMakerOrder.get_instance(),
                        sconscript, build_root, variants, duplicate)


def make_variant_builders(variant=None):
    '''Generate SCons builders for the variant.'''
    exec_variant_builder_makers(BuilderMakerOrder.get_instance(), variant)
