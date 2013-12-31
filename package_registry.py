# Copyright (c) 2013 Che-Liang Chiou

from SCons.Script import Environment

from scons_package.label import PackageName


class PackageAttributes(object):
    '''A homogeneous trie of package attributes.'''

    def __init__(self, attr_class):
        self.attr_class = attr_class
        self.package_trie = PackageTrie()
        self.attrs = {}
        self._default = None

    def get_default(self):
        return self._default

    def set_default(self, default):
        assert isinstance(default, self.attr_class)
        self._default = default

    default = property(get_default, set_default)

    def add(self, package_name, value):
        assert isinstance(package_name, PackageName)
        assert isinstance(value, self.attr_class)
        if package_name in self.attrs:
            raise KeyError('overwrite package: %s' % package_name)
        self.package_trie.add(package_name)
        self.attrs[package_name] = value

    def search(self, package_name):
        assert isinstance(package_name, PackageName)
        pkg_name = self.package_trie.search(package_name)
        if pkg_name is not None:
            return self.attrs[pkg_name]
        if self._default is not None:
            return self._default
        raise KeyError(str(package_name))


class PackageVariantRegistry(PackageAttributes):

    Instance = None

    @classmethod
    def get_instance(cls):
        if cls.Instance is None:
            cls.Instance = cls()
        return cls.Instance

    def __init__(self):
        super(PackageVariantRegistry, self).__init__(str)


class PackageEnvironmentRegistry(PackageAttributes):

    Instance = None

    @classmethod
    def get_instance(cls):
        if cls.Instance is None:
            cls.Instance = cls()
        return cls.Instance

    def __init__(self):
        super(PackageEnvironmentRegistry, self).__init__(Environment)


class PackageTrie:

    class Node:
        def __init__(self, package_name):
            assert (package_name is None or
                    isinstance(package_name, PackageName))
            self.package_name = package_name
            self.edges = {}

    def __init__(self):
        self.root = PackageTrie.Node(None)

    def add(self, package_name):
        assert isinstance(package_name, PackageName)
        self._add(self.root, '', package_name)

    def _add(self, node, path, package_name):
        assert package_name.path.startswith(path)
        for component, child in node.edges.items():
            child_path = path + component
            # Same package
            if child_path == package_name.path:
                assert package_name == child.package_name
                break
            # package_name is shorter
            if child_path.startswith(package_name.path):
                pkg_path = package_name.path
                prefix = pkg_path[len(path):]
                suffix = child_path[len(pkg_path):]
                new_node = PackageTrie.Node(package_name)
                node.edges.pop(component)
                node.edges[prefix] = new_node
                new_node.edges[suffix] = child
                break
            # child_path is shorter
            if package_name.path.startswith(child_path):
                self._add(child, child_path, package_name)
                break
        # package_name does not match any child
        else:
            component = package_name.path[len(path):]
            assert component not in node.edges
            node.edges[component] = PackageTrie.Node(package_name)

    def search(self, target):
        assert isinstance(target, (PackageName, str))
        if isinstance(target, PackageName):
            target = target.path
        return self._search(self.root, '', target).package_name

    def _search(self, node, path, target):
        assert target.startswith(path)
        for component, child in node.edges.items():
            child_path = path + component
            # Same package
            if child_path == target:
                return child
            # target is shorter
            if child_path.startswith(target):
                continue
            # child_path is shorter
            if target.startswith(child_path):
                return self._search(child, child_path, target)
        # target does not match any child
        else:
            return node
