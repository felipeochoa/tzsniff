"""
This module comes up with test vectors that can be used to quickly
sniff a user's time zone. It generates a decision tree that selects a
time zone based on the the UTC offsets of various points in time.

"""

import attr
from collections import OrderedDict
from datetime import datetime
import json
import math
import os.path
import pytz

dirname = os.path.dirname(__file__)


def offset_min(tz, test_point):
    "Return the offset from UTC for a test point in minutes."
    return tz.utcoffset(test_point, is_dst=False).total_seconds() / 60


def dedup(d, preferred):
    """
    Remove duplicate entries from a dict.

    Keys in preferred will be included in the resulting dict if possible.
    (Later keys are favored over earlier ones.)

    """
    rev = {v: k for k, v in d.items()}
    for key in preferred:
        rev[d[key]] = key
    return {k: v for v, k in rev.items()}


def maybe_int(v):
    "If v is a float representing an integer, convert to integer."
    if v.is_integer():
        return int(v)
    return v


@attr.s
class Table:
    data = attr.ib()  # list of columns
    row_names = attr.ib()  # list of row names

    def __len__(self):
        return len(self.row_names)

    def partition(self, col_ix):
        "Return new tables partitioned using column col_ix."
        return {val: self.get_partition(col_ix, val)
                for val in set(self.data[col_ix])}

    def get_partition(self, col_ix, val):
        indexes = [i for i, v in enumerate(self.data[col_ix]) if v == val]
        data = [[col[i] for i in indexes] for col in self.data]
        row_names = [self.row_names[i] for i in indexes]
        return Table(data=data, row_names=row_names)

    def get_entropy(self, col_ix):
        "Returns the entropy of a certain table column."
        column = self.data[col_ix]
        num_rows = len(column)
        density = (column.count(v) / num_rows for v in set(column))
        return -sum(p * math.log2(p) for p in density)

    def max_entropy_split(self):
        "Find the max. entropy column and partition the table based on it."
        col_ix = max(range(len(self.data)), key=self.get_entropy)
        return (col_ix, self.partition(col_ix))


@attr.s
class Node:
    naive_dt = attr.ib()
    children = attr.ib()

    def test(self, tz):
        if isinstance(self.children, str):
            return self.children
        return self.children[offset_min(tz, self.naive_dt)].test(tz)

    def max_depth(self):
        if isinstance(self.children, str):
            return 0
        return 1 + max(c.max_depth() for c in self.children.values())

    def serialize(self):
        if isinstance(self.children, str):
            return self.children
        ret = OrderedDict()
        ret["testPoint"] = self.naive_dt.isoformat()
        ret["children"] = {maybe_int(v): c.serialize()
                           for v, c in self.children.items()}
        return ret


print("Generating test points")
test_points = [datetime(year, month, 1, 0, 27)
               for year in range(2000, 2018) for month in range(1, 13)]
all_timezones = sorted(set(sum(pytz.country_timezones.values(), [])))
print("Obtained %d timezones from pytz" % len(all_timezones))
with open(os.path.join(dirname, 'equivalencies.json'), 'rt') as f:
    preferred_timezones = list(json.load(f))
vectors = dedup({
    tz: tuple(offset_min(pytz.timezone(tz), point) for point in test_points)
    for tz in all_timezones
}, preferred_timezones)
unique_timezones = sorted(vectors)
print("Found %d unique timezones based on test points" % len(unique_timezones))

parent_table = Table(
    data=tuple(map(tuple, zip(*(vectors[tz] for tz in unique_timezones)))),
    row_names=unique_timezones,
)


def make_tree(table: Table):
    if len(table) == 1:
        return Node(naive_dt=None, children=table.row_names[0])
    test_point_ix, subtables = table.max_entropy_split()
    return Node(
        naive_dt=test_points[test_point_ix],
        children={val: make_tree(subt) for val, subt in subtables.items()}
    )


tree = make_tree(parent_table)
print('Generated decision tree with depth %d' % tree.max_depth())
equivalencies = OrderedDict()
for tz in unique_timezones:
    equivalencies[tz] = []
for tzname in all_timezones:
    if tzname in equivalencies:
        continue
    equivalencies[tree.test(pytz.timezone(tzname))].append(tzname)

for k, e in tuple(equivalencies.items()):
    if e:
        e.sort()
    else:
        del equivalencies[k]

with open(os.path.join(dirname, 'js', 'tz-tree.json'), 'wt') as f:
    json.dump(tree.serialize(), f, indent=2)
    f.write('\n')
print('Wrote tz-tree.json')

with open(os.path.join(dirname, 'js', 'tz-tree.min.json'), 'wt') as f:
    json.dump(tree.serialize(), f, indent=None, separators=(',', ':'))
print('Wrote tz-tree.min.json')

with open(os.path.join(dirname, 'equivalencies.json'), 'wt') as f:
    json.dump(equivalencies, f, indent=2)
    f.write('\n')
print('Wrote equivalencies.json')
