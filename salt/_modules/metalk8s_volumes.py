# coding: utf-8
'''Metalk8s volumes module.'''

import json
import re
import os

import logging

from salt.exceptions import CommandExecutionError

log = logging.getLogger(__name__)


__virtualname__ = 'metalk8s_volumes'


def __virtual__():
    return __virtualname__


def sparse_file_exists(path, capacity):
    """Check if the sparse file exists and has the expected size.

    Args:
        path     (str): path of the sparse file
        capacity (str): expected size of the sparse file

    Returns:
        bool: True if the sparse file exists and has the right capacity.

    CLI Example:

    .. code-block:: bash

        salt '*' metalk8s_volumes.sparse_file_exists /path/to/sparsefile 1Gi
    """
    size = _quantity_to_bytes(capacity)
    return os.path.isfile(path) and os.path.getsize(path) == size


def sparse_file_create(path, capacity):
    """Create a sparse file with the specified capacity.

    Args:
        path     (str): path of the sparse file
        capacity (str): expected size of the sparse file

    Returns:
        None

    CLI Example:

    .. code-block:: bash

        salt '*' metalk8s_volumes.sparse_file_create /path/to/sparsefile 1Gi
    """
    # Try to create a sparse file, don't clobber existing one!
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except OSError as exn:
        raise Exception('cannot create sparse file at {}: {}'.format(path, exn))
    # Set the sparse file capacity.
    try:
        size = _quantity_to_bytes(capacity)
        os.ftruncate(fd, size)
    except OSError as exn:
        raise Exception('cannot resize sparse file at {}: {}'.format(path, exn))
    finally:
        os.close(fd)


def sparse_loop_is_initialized(path):
    """Check if the sparse loop device is initialized.

    A sparse loop device is initialized when a sparse file is associated to a
    loop device.

    Args:
        path (str): path of the sparse file

    Returns:
        bool: True if a loop device is associated to the sparse file

    CLI Example:

    .. code-block:: bash

        salt '*' metalk8s_volumes.sparse_loop_is_initialized /path/to/sparsefile
    """
    # Recent losetup support `--json` but not the one shipped with CentOS.
    command = ' '.join(['losetup', '--associated', path])
    pattern = r'\({}\)'.format(re.escape(path))
    result  = _run_cmd(command)
    return re.search(pattern, result['stdout']) is not None


def sparse_loop_initialize(path):
    """Initialize a sparse loop device.

    A sparse loop device is initialized when a sparse file is associated to a
    loop device.

    Args:
        path (str): path of the sparse file

    Returns:
        str: path to the associated loop device

    CLI Example:

    .. code-block:: bash

        salt '*' metalk8s_volumes.sparse_loop_initialize /path/to/sparsefile
    """
    # Recent losetup support `--nooverlap` but not the one shipped with CentOS.
    command = ' '.join(['losetup', '--find', '--partscan', '--show', path])
    result  = _run_cmd(command)
    return result['stdout'].strip()


def is_formatted(name):
    """Check if the given volume is formatted.

    Args:
        name (str): volume name

    Returns:
        bool: True if the volume is already formatted, otherwise False

    CLI Example:

    .. code-block:: bash

        salt '*' metalk8s_volumes.volume_is_formatted example-volume
    """
    volume = __pillar__['metalk8s']['volumes'].get(name)
    if volume is None:
        raise ValueError('volume `{}` not found in pillar'.format(name))
    path = _get_block_device_path(volume)
    storage_class = volume['spec']['storageClassName']
    fs_type = storage_class['parameters']['fsType']
    return __salt__['disk.fstype'](path) == fs_type


def mkfs(name):
    """Format the given volume.

    Args:
        name (str): volume name

    Returns:
        None

    CLI Example:

    .. code-block:: bash

        salt '*' metalk8s_volumes.mkfs example-volume
    """
    volume = __pillar__['metalk8s']['volumes'].get(name)
    if volume is None:
        raise ValueError('volume `{}` not found in pillar'.format(name))
    storage_class = volume['spec']['storageClassName']
    mkfs_options = json.loads(storage_class['parameters']['mkfsOptions'])
    command = ['mkfs']
    command.extend(['-t', storage_class['parameters']['fsType']])
    command.extend(['-U', volume['metadata']['uid']])
    command.extend(mkfs_options)
    command.append(_get_block_device_path(volume))
    _run_cmd(' '.join(command))


def _run_cmd(cmd):
    """Execute the given `cmd` command and return its result.

    Raise `CommandExecutionError` if the command failed.

    Args:
        cmd  (str): command to execute

    Returns:
        dict: the command result (stderr, stdout, retcode, …)
    """
    ret = __salt__['cmd.run_all'](cmd)
    if ret.get('retcode', 0) != 0:
        raise CommandExecutionError(
            'error while trying to run `{0}`: {1}' .format(cmd, ret['stderr'])
        )
    return ret


def _quantity_to_bytes(quantity):
    """Return a quantity with a unit converted into a number of bytes.

    Examples:
    >>> quantity_to_bytes('42Gi')
    45097156608
    >>> quantity_to_bytes('100M')
    100000000
    >>> quantity_to_bytes('1024')
    1024

    Args:
        quantity (str): a quantity, composed of a count and an optional unit

    Returns:
        int: the capacity (in bytes)
    """
    UNIT_FACTOR = {
      None:  1,
      'Ki':  2 ** 10,
      'Mi':  2 ** 20,
      'Gi':  2 ** 30,
      'Ti':  2 ** 40,
      'Pi':  2 ** 50,
      'k':  10 ** 3,
      'M':  10 ** 6,
      'G':  10 ** 9,
      'T':  10 ** 12,
      'P':  10 ** 15,
    }
    size_regex = r'^(?P<size>[1-9][0-9]*)(?P<unit>[kKMGTP]i?)?$'
    match = re.match(size_regex, quantity)
    assert match is not None, 'invalid resource.Quantity value'
    size = int(match.groupdict()['size'])
    unit = match.groupdict().get('unit')
    return size * UNIT_FACTOR[unit]


def _get_block_device_path(volume):
    """Return the path to the backing block device.

    Args:
        volume (dict): a Volume object

    Returns:
        str: path to the block device
    """
    if 'rawBlockDevice' in volume['spec']:
        return volume['spec']['rawBlockdevice']['devicePath']
    elif 'sparseLoopDevice' in volume['spec']:
        volume_name = volume['metadata']['name']
        path = '/var/lib/metalk8s/storage/sparse/{}'.format(volume_name)
        command = ' '.join(['losetup', '--associated', path])
        result  = _run_cmd(command)
        # e.g.: /dev/loop0: [2049]:184645 (/var/lib/metalk8s/storage/sparse/vol)
        device_path, _, _ = result['stdout'].partition(':')
        return device_path
    else:
        raise ValueError('unsupported Volume type')
