# Copyright (c) 2013 Che-Liang Chiou

import os
import re


def glob(pattern, recursive=False):
    pattern = re.compile(pattern)
    paths = []
    if recursive:
        for dirpath, _, filenames in os.walk(os.path.curdir):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                path = os.path.relpath(path, os.path.curdir)
                if pattern.search(path):
                    paths.append(path)
    else:
        for filename in os.listdir(os.path.curdir):
            if pattern.search(filename):
                paths.append(filename)
    return paths
