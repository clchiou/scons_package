# Copyright (c) 2013 Che-Liang Chiou

from collections import defaultdict
import os
import sys

from SCons.Script import SConscript

from scons_package import builder_maker
from scons_package.builder_maker_registry import BuilderMakerRegistry
from scons_package.package_registry import PackageEnvironmentRegistry
from scons_package.package_registry import PackageVariantRegistry
from scons_package.utils import topology_sort


def exec_builder_makers(build_order,
                        sconscript, build_root, variants, duplicate):
    # If sconscript is None, then build_root and variants should be empty.
    assert sconscript is not None or (build_root is None and not variants)
    # If build_root is None, then variants should be empty.
    assert build_root is not None or not variants

    if sconscript is None:
        build_order.sort_by(variants=None)
        exec_variant_builder_makers(build_order, None)
        return

    if build_root is None:
        build_order.sort_by(variants=None)
        SConscript(sconscript, exports={'variant': None})
        return

    if not variants:
        build_order.sort_by(variants=None)
        SConscript(sconscript, variant_dir=build_root, duplicate=duplicate,
                   exports={'variant': None})
        return

    build_order.sort_by(variants=variants)
    for variant in build_order.get_sorted_variants():
        variant_dir = os.path.join(build_root, variant)
        SConscript(sconscript, variant_dir=variant_dir, duplicate=duplicate,
                   exports={'variant': variant})


def exec_variant_builder_makers(build_order, variant):
    for rule in build_order.get_rules(variant):
        builder_maker.builder_maker(rule, build_order.bmreg, build_order.pereg)


class BuilderMakerOrder:

    Instance = None

    @classmethod
    def get_instance(cls):
        if cls.Instance is None:
            cls.Instance = cls(BuilderMakerRegistry.get_instance(),
                               PackageVariantRegistry.get_instance(),
                               PackageEnvironmentRegistry.get_instance())
        return cls.Instance

    def __init__(self, bmreg, pvreg, pereg):
        assert isinstance(bmreg, BuilderMakerRegistry)
        assert isinstance(pvreg, PackageVariantRegistry)
        assert isinstance(pereg, PackageEnvironmentRegistry)
        self.bmreg = bmreg
        self.pvreg = pvreg
        self.pereg = pereg
        self.sorted_variants = None
        self.variant_rules = None

    def sort_by(self, variants):
        bmreg = self.bmreg
        pvreg = self.pvreg
        rules = bmreg.rules
        self._check_depends(rules)

        if variants is None:
            self.sorted_variants = None
            self.variant_rules = {None: rules.get_sorted_rules()}
            return

        graph = defaultdict(set)
        for label_from in rules:
            variant_from = self._get_variant(bmreg, pvreg, label_from)
            for label_to in rules[label_from].depends:
                variant_to = self._get_variant(bmreg, pvreg, label_to)
                if variant_from != variant_to:
                    graph[variant_from].add(variant_to)

        def get_neighbors(variant):
            return graph[variant]
        self.sorted_variants = topology_sort(variants, get_neighbors)

        self.variant_rules = defaultdict(list)
        for rule in rules.get_sorted_rules():
            variant = self._get_variant(bmreg, pvreg, rule.name)
            self.variant_rules[variant].append(rule)
        assert len(variants) == len(self.variant_rules)

    def get_sorted_variants(self):
        assert self.sorted_variants is not None
        return self.sorted_variants

    def get_rules(self, variant):
        assert self.variant_rules is not None
        return self.variant_rules[variant]

    @staticmethod
    def _check_depends(rules):
        okay = True
        for name, depend in rules.get_missing_dependencies():
            sys.stderr.write('%s depends on non-existing %s\n' %
                             (name, depend))
            sys.stderr.write('Targets in package %s:\n' % depend.package_name)
            for label in rules:
                if label.package_name == depend.package_name:
                    sys.stderr.write('    %s\n' % label)
            sys.stderr.write('\n')
            okay = False
        if not okay:
            raise RuntimeError('missing dependencies')

    @staticmethod
    def _get_variant(bmreg, pvreg, label):
        # Retrieve variant from rule/package/default (in that order)
        try:
            return bmreg.get_attr(label, builder_maker.VARIANT)
        except KeyError:
            return pvreg.search(label.package_name)
