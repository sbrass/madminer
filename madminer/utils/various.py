from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import six
import os
from subprocess import Popen, PIPE
import io
import numpy as np
import math
from collections import OrderedDict

from madminer import __version__


def general_init(debug=False):
    logging.basicConfig(format='%(asctime)s  %(message)s', datefmt='%H:%M')
    logging.getLogger().setLevel(logging.DEBUG if debug else logging.INFO)

    logging.info('')
    logging.info('------------------------------------------------------------')
    logging.info('|                                                          |')
    logging.info('|  MadMiner v{}|'.format(__version__.ljust(46)))
    logging.info('|                                                          |')
    logging.info('|           Johann Brehmer, Kyle Cranmer, and Felix Kling  |')
    logging.info('|                                                          |')
    logging.info('------------------------------------------------------------')
    logging.info('')


def call_command(cmd, log_file=None):
    if log_file is not None:
        with io.open(log_file, 'wb') as log:
            proc = Popen(cmd, stdout=log, stderr=log, shell=True)
            _ = proc.communicate()
            exitcode = proc.returncode

        if exitcode != 0:
            raise RuntimeError(
                'Calling command {} returned exit code {}. Output in file {}.'.format(
                    cmd, exitcode, log_file
                )
            )
    else:
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = proc.communicate()
        exitcode = proc.returncode

        if exitcode != 0:
            raise RuntimeError(
                'Calling command {} returned exit code {}.\n\nStd output:\n\n{}Error output:\n\n{}'.format(
                    cmd, exitcode, out, err
                )
            )

    return exitcode


def create_missing_folders(folders):
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

        elif not os.path.isdir(folder):
            raise OSError('Path {} exists, but is no directory!'.format(folder))


def format_benchmark(parameters, precision=2):
    output = ''

    for i, (key, value) in enumerate(six.iteritems(parameters)):
        if i > 0:
            output += ', '

        value = float(value)

        if value < 2. * 10. ** (- precision) or value > 100.:
            output += str(key) + (' = {0:.' + str(precision) + 'e}').format(value)
        else:
            output += str(key) + (' = {0:.' + str(precision) + 'f}').format(value)

    return output


def shuffle(*arrays):
    """ Shuffles multiple arrays simultaneously"""

    permutation = None
    n_samples = None
    shuffled_arrays = []

    for i, a in enumerate(arrays):
        if a is None:
            shuffled_arrays.append(a)
            continue

        if permutation is None:
            n_samples = a.shape[0]
            permutation = np.random.permutation(n_samples)

        assert a.shape[0] == n_samples
        shuffled_a = a[permutation]
        shuffled_arrays.append(shuffled_a)

    return shuffled_arrays


def balance_thetas(theta_sets_types, theta_sets_values):
    """ Repeats theta values such that all thetas lists have the same length """

    n_sets = max([len(thetas) for thetas in theta_sets_types])

    for i, (types, values) in enumerate(zip(theta_sets_types, theta_sets_values)):
        assert len(types) == len(values)
        n_sets_before = len(types)

        if n_sets_before != n_sets:
            theta_sets_types[i] = [types[i % n_sets_before] for i in range(n_sets)]
            theta_sets_values[i] = [values[i % n_sets_before] for i in range(n_sets)]

    return theta_sets_types, theta_sets_values


def load_and_check(filename, warning_threshold=1.e9):
    if filename is None:
        return None

    data = np.load(filename)

    n_nans = np.sum(np.isnan(data))
    n_infs = np.sum(np.isinf(data))
    n_finite = np.sum(np.isfinite(data))

    if n_nans + n_infs > 0:
        logging.warning('Warning: file %s contains %s NaNs and %s Infs, compared to %s finite numbers!',
                        filename, n_nans, n_infs, n_finite)

    smallest = np.nanmin(data)
    largest = np.nanmax(data)

    if np.abs(smallest) > warning_threshold or np.abs(largest) > warning_threshold:
        logging.warning('Warning: file %s has some large numbers, rangin from %s to %s',
                        filename, smallest, largest)

    return data

def math_commands():
    """ Provides OrderedDict() with math commands - for some reason I need this when using eval """
    
    math_commands_collection = OrderedDict()
    math_commands_collection['exp']=math.exp
    math_commands_collection['sin']=math.sin
    math_commands_collection['cos']=math.cos
    math_commands_collection['tan']=math.tan
    math_commands_collection['acos']=math.acos
    math_commands_collection['asin']=math.asin
    math_commands_collection['atan']=math.atan

    return math_commands_collection
