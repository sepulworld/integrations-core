# (C) Datadog, Inc. 2019
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import linecache
import os
from datetime import datetime

from binary import BinaryUnits, convert_units

try:
    import tracemalloc
except ImportError:
    tracemalloc = None

# The order matters
VALID_PACKAGE_ROOTS = ('datadog_checks', 'site-packages', 'lib', 'Lib')


def get_sign(n):
    return '-' if n < 0 else '+'


def get_timestamp_filename(prefix):
    return '{}_{}'.format(prefix, datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S_%f'))


def parse_package_path(path):
    # If possible, replace `/path/to/<PACKAGES_ROOT>/package/file.py` with `package/file.py`
    # where the root is either:
    #
    # 1. datadog_checks namespace
    # 2. site-packages
    # 3. stdlib
    path_parts = path.split(os.sep)

    # We reuse the already split path to avoid a complex regular expression
    package_root = None
    for valid_root in VALID_PACKAGE_ROOTS:
        if valid_root in path_parts:
            package_root = valid_root
            break

    if package_root:
        check_package_parts = path_parts[path_parts.index(package_root) + 1:]
        if check_package_parts:
            path = os.sep.join(check_package_parts)

    return path


def get_unit(unit):
    return getattr(BinaryUnits, unit.upper().replace('I', ''), BinaryUnits.B)


def format_units(unit, amount, unit_repr):
    # Dynamic based on the number of bytes
    if unit is None:
        unit = get_unit(unit_repr)

    if unit < BinaryUnits.KB:
        return '%d' % amount, unit_repr
    elif unit < BinaryUnits.MB:
        return '%.2f' % amount, unit_repr
    else:
        return '%.3f' % amount, unit_repr


def get_unit_formatter(unit):
    if unit == 'highest':
        unit = None
    else:
        unit = get_unit(unit)

    return lambda n: format_units(unit, *convert_units(n, to=unit))


def write_pretty_top(path, snapshot, unit_formatter, key_type, limit):
    top_stats = snapshot.statistics(key_type, cumulative=False)

    with open(path, 'w', encoding='utf-8') as f:
        f.write('Top {} lines\n'.format(limit))

        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]

            amount, unit = unit_formatter(stat.size)
            f.write(
                '\n#{}: {}:{}: {} {}\n'.format(index, parse_package_path(frame.filename), frame.lineno, amount, unit)
            )

            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                f.write('    {}\n'.format(line))

        f.write('\n')

        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            amount, unit = unit_formatter(size)
            f.write('{} other: {} {}\n'.format(len(other), amount, unit))

        total = sum(stat.size for stat in top_stats)
        amount, unit = unit_formatter(total)
        f.write('Total allocated size: {} {}\n'.format(amount, unit))


def write_pretty_diff(path, current_snapshot, previous_snapshot, unit_formatter, key_type, limit):
    top_stats = current_snapshot.compare_to(previous_snapshot, key_type=key_type, cumulative=False)

    with open(path, 'w', encoding='utf-8') as f:
        f.write('Top {} line diffs\n'.format(limit))

        index = 0
        for stat in top_stats[:limit]:
            # Disregard lines that have no diff as the top lines are already shown by the snapshot files
            if not stat.size_diff:
                continue

            index += 1
            frame = stat.traceback[0]

            amount, unit = unit_formatter(abs(stat.size_diff))
            f.write(
                '\n#{}: {}:{}: {}{} {}\n'.format(
                    index,
                    parse_package_path(frame.filename),
                    frame.lineno,
                    get_sign(stat.size_diff),
                    amount,
                    unit,
                )
            )

            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                f.write('    {}\n'.format(line))

        f.write('\n')

        other = top_stats[limit:]
        if other:
            size = sum(stat.size_diff for stat in other)
            amount, unit = unit_formatter(abs(size))
            f.write('{} other: {}{} {}\n'.format(len(other), get_sign(size), amount, unit))

        total = sum(stat.size_diff for stat in top_stats)
        amount, unit = unit_formatter(abs(total))
        f.write('Total difference: {}{} {}\n'.format(get_sign(total), amount, unit))


def profile_memory(f, config, args=(), kwargs=None):
    """
    This will track all memory (de-)allocations that occur during the lifetime of function ``f``.
    The only assumption is that the ``config`` dictionary has an entry ``profile_memory`` that
    points to an existing directory with which to output the information for later consumption.

    :param f:
    :param config:
    :param args:
    :param kwargs:
    :return:
    """
    location = config['profile_memory']
    if kwargs is None:
        kwargs = {}

    depth = config.get('profile_memory_depth', 25)
    tracemalloc.start(depth)

    try:
        f(*args, **kwargs)
        snapshot = tracemalloc.take_snapshot()
    finally:
        tracemalloc.stop()

    verbose = bool(config.get('profile_memory_verbose', 0))
    if not verbose:
        snapshot = snapshot.filter_traces(
            (
                tracemalloc.Filter(False, '<frozen importlib._bootstrap>'),
                tracemalloc.Filter(False, '<unknown>'),
                tracemalloc.Filter(False, __file__),
            )
        )

    sort_by = config.get('profile_memory_sorting', 'lineno')
    lines = config.get('profile_memory_lines', 40)
    unit = config.get('profile_memory_unit', 'highest')
    unit_formatter = get_unit_formatter(unit)

    # First, write the prettified snapshot
    snapshot_dir = os.path.join(location, 'snapshots')
    if not os.path.isdir(snapshot_dir):
        os.makedirs(snapshot_dir)

    new_snapshot = os.path.join(snapshot_dir, get_timestamp_filename('snapshot'))
    write_pretty_top(new_snapshot, snapshot, unit_formatter, sort_by, lines)

    # Then, compute the diff if there was a previous run
    previous_snapshot_dump = os.path.join(location, 'last-snapshot')
    if os.path.isfile(previous_snapshot_dump):
        diff_dir = os.path.join(location, 'diffs')
        if not os.path.isdir(diff_dir):
            os.makedirs(diff_dir)

        previous_snapshot = tracemalloc.Snapshot.load(previous_snapshot_dump)

        # and write it
        new_diff = os.path.join(diff_dir, get_timestamp_filename('diff'))
        write_pretty_diff(new_diff, snapshot, previous_snapshot, unit_formatter, sort_by, lines)

    # Finally, dump the current snapshot for doing a diff on the next run
    snapshot.dump(previous_snapshot_dump)
