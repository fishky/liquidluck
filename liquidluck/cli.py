#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import shutil
import argparse
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

from liquidluck.utils import import_module, walk_dir
from liquidluck.ns import namespace
from liquidluck import logger
from liquidluck.readers import detect_reader

ROOT = os.path.dirname(__file__)
namespace.root = ROOT
namespace.posts = []
namespace.files = []


def init(filepath):
    config = ConfigParser()
    config.read(filepath)
    namespace.site.update(config.items('site'))
    namespace.context.update(config.items('context'))
    for sec in ('writers', 'readers', 'filters'):
        if config.has_section(sec):
            namespace[sec].update(config.items(sec))
    namespace.projectdir = os.getcwd()

    postdir = os.path.join(namespace.projectdir,
                           namespace.site.get('postdir','content'))
    for f in walk_dir(postdir):
        reader = detect_reader(f)
        if reader:
            post = reader.render()
            if post:
                # ignore invalid post
                namespace.posts.append(post)
        else:
            namespace.files.append(f)

    return config


def build(config_file):
    begin = time.time()
    if not os.path.exists(config_file):
        answer = raw_input('This is not a Felix Felicis repo, '
                           'would you like to create one?(Y/n) ')
        if answer.lower() == 'n':
            sys.exit(1)
            return
        return create()

    init(config_file)

    logger.info('Starting readers')
    for reader in namespace.readers.values():
        import_module(reader)().start()

    logger.info('Starting writters')
    for writer in namespace.writers.values():
        import_module(writer)().start()

    logger.info('Running writters')
    for writer in namespace.writers.values():
        import_module(writer)().run()
    
    for error in namespace.errors:
        logger.error('Invalid Post: %s' % error)

    end = time.time()
    logger.info('Total time: %s' % (end - begin))
    return


def create(config_file='config.ini'):
    shutil.copy(os.path.join(ROOT, 'config.ini'), config_file)
    config = init(config_file)
    cwd = os.getcwd()
    dest = os.path.join(cwd, namespace.site.get('staticdir', 'static'))
    if not os.path.exists(dest):
        shutil.copytree(os.path.join(ROOT, '_static'), dest)
    dest = os.path.join(cwd, namespace.site.get('template', '_templates'))
    if not os.path.exists(dest):
        #shutil.copytree(os.path.join(ROOT, '_templates'), dest)
        os.makedirs(dest)
    dest = os.path.join(cwd, namespace.site.get('postdir', 'content'))
    if not os.path.exists(dest):
        os.makedirs(dest)
    print('Felix Felicis Repo Created')
    return


def main():
    parser = argparse.ArgumentParser(
        prog='liquidluck',
        description=('Felix Felicis, aka liquidluck,'
                     'is a static weblog generator'),
    )
    parser.add_argument('command', nargs='*', type=str, default='build',
                        metavar='command',
                        help='liquidluck commands: create, build etc.'
                       )
    parser.add_argument('-f', '--config', dest='config', default='config.ini',
                        metavar='config.ini')
    args = parser.parse_args()

    def run_command(cmd):
        if cmd == 'build':
            return build(args.config)
        if cmd == 'create':
            return create(args.config)
        config = init(args.config)
        if not config.has_section('commands'):
            return
        for k, v in config.items('commands'):
            if args.command == k:
                return import_module(v)(args.config)

    if isinstance(args.command, basestring):
        return run_command(args.command)
    if isinstance(args.command, list):
        for cmd in args.command:
            run_command(cmd)


if '__main__' == __name__:
    main()
