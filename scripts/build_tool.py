#!/usr/bin/env python3

import argparse

import config

from lib.tool import ToolName
from build.build import rebuild_tool


def main():
    arg_parser = argparse.ArgumentParser('Third party libraries building tool')

    arg_parser.add_argument('name',
                            type=ToolName,
                            choices=list(ToolName),
                            help='Select tool to build')

    arg_parser.add_argument('-j', help='Number of jobs to build',
                            type=int, default=config.BUILD.jobs)

    arg_parser.add_argument('--cc', help='Path to the C compiler',
                            type=str, default=config.BUILD.cc)

    arg_parser.add_argument('--cxx', help='Path to the C++ compiler',
                            type=str, default=config.BUILD.cxx)

    arg_parser.add_argument('--cudacxx', help='Path to the Cuda compiler',
                            type=str, default=config.BUILD.cudacxx)

    args = arg_parser.parse_args()

    config.BUILD.jobs = args.j
    config.BUILD.cxx = args.cxx
    config.BUILD.cc = args.cc
    config.BUILD.cudacxx = args.cudacxx

    rebuild_tool(args.name)


if __name__ == '__main__':
    main()
