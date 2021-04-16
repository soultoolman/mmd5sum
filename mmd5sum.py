# -*- coding: utf-8 -*-
import sys
import codecs
import subprocess as sp
from shutil import which
from os.path import join
import multiprocessing as mp
from functools import partial

import click
import scandir


def get_all_files(directory):
    all_files = []
    for root, dirs, files in scandir.walk(directory):
        for file in files:
            all_files.append(join(root, file))
    return all_files


def md5sum(file, md5sum_command='md5sum'):
    proc = sp.run([md5sum_command, file], stdout=sp.PIPE)
    return file, proc.stdout.decode('utf-8').strip().split(maxsplit=1)[0]


def validate_infile(ctx, param, value):
    if value is None:
        return {}
    try:
        exists_hexes = {}
        with codecs.open(value) as fp:
            for line in fp:
                file, hex = line.rstrip().split('\t')
                exists_hexes[file] = hex
        return exists_hexes
    except Exception:
        raise click.BadParameter(
            'invalid infile %s, should contains only two columns, '
            'the first column is file, the second column is hex' % value
        )


def validate_md5sum_command(ctx, param, value):
    command = which(value)
    if not command:
        raise click.BadParameter(
            'the command using to calculate MD5 does not exists: %s' % value
        )
    return command


@click.command()
@click.option(
    '-d', '--directory', type=click.Path(exists=True), default='.', show_default=True,
    help='directory that contains multiple files to calculate MD5, can have sub-directories'
)
@click.option(
    '-i', '--infile', 'exists_hexes', required=False, callback=validate_infile,
    help=('MD5s file that has calculated already,'
          'if you have some MD5s calculated already, '
          'specify it can avoid calculating again, '
          'this file must contains only two columns, '
          'the first is file path, the second is MD5 hex string')
)
@click.option(
    '-o', '--outfile', type=click.Path(exists=False),
    default='md5.txt', show_default=True,
    help='where you want save your MD5s'
)
@click.option(
    '-p', '--processes', type=int, default=4,
    show_default=True, help='how man processes you want to use'
)
@click.option(
    '-m', '--md5sum-command', default='md5sum', show_default=True,
    callback=validate_md5sum_command, help='the command to calculate MD5 hex string'
)
def main(directory, exists_hexes, outfile, processes, md5sum_command):
    """
    calculate multiple MD5s using multiple processes.
    """
    try:
        all_files = get_all_files(directory)
        new_files = []
        hexes = {}
        new_hexes = {}

        # filter files that calculated
        for file in all_files:
            if file in exists_hexes:
                hexes[file] = exists_hexes[file]
            else:
                new_files.append(file)

        # calculate
        total = len(new_files)
        if total > 0:
            current = 0
            with mp.Pool(processes) as pool:
                for file, hex in pool.imap_unordered(
                    partial(md5sum, md5sum_command=md5sum_command),
                    new_files
                ):
                    current += 1
                    new_hexes[file] = hex
                    sys.stderr.write('\r%.2f%%' % (round(current/total, 4) * 100))

        # write results to file
        with codecs.open(outfile, 'w') as fp:
            for file, hex in hexes.items():
                fp.write('%s\t%s\n' % (file, hex))
            for file, hex in new_hexes.items():
                fp.write('%s\t%s\n' % (file, hex))
    except Exception as e:
        raise click.UsageError(
            'Unknown error occurred: %s' % e
        )


if __name__ == '__main__':
    main()
