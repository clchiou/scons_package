# Copyright (c) 2013 Che-Liang Chiou

from collections import defaultdict, deque
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


def topology_sort(nodes, get_neighbors):
    graph = {}
    reverse_graph = defaultdict(deque)
    ready = deque()
    for node in nodes:
        neighbors = set(get_neighbors(node))
        neighbors.discard(node)  # Remove self-reference
        graph[node] = neighbors
        for neighbor in neighbors:
            reverse_graph[neighbor].append(node)
        if not neighbors:
            ready.append(node)

    output = []
    while ready:
        node = ready.popleft()
        output.append(node)
        for reverse_neighbor in reverse_graph[node]:
            neighbors = graph[reverse_neighbor]
            neighbors.remove(node)
            if not neighbors:
                ready.append(reverse_neighbor)
    if len(output) != len(graph):
        raise ValueError('incorrect topology')

    return output
