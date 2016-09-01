#!/usr/bin/env python

"""Manage file conversions."""

from __future__ import print_function

import argparse
import ConfigParser
import json
import os
import re
import subprocess
import sys


DEFAULT_RULES = os.path.join(os.path.dirname(__file__), "rules.ini")
BIN_PATH = os.path.join(os.path.dirname(__file__), "bin")


def log_get_missing(log):
    res = []
    cre = re.compile(r"^.* Error: File `(.*)' not found\.$")
    with open(log, "r") as f:
        for line in f.readlines():
            m = cre.match(line)
            if m is None:
                continue
            res.append(m.group(1))
    return res


def search_converters(path):
    converters = {}
    parser = ConfigParser.ConfigParser()

    for elem in path:
        parser.read(elem)

    # post-process sections
    for sec in parser.sections():
        conv = dict(parser.items(sec))
        if "source" not in conv:
            continue
        if "target" not in conv:
            continue
        conv["target"] = re.compile(conv["target"])
        if "command" not in conv:
            continue
        conv["command"] = json.loads(conv["command"])
        if "message" not in conv:
            conv["message"] = "Converting {source} to {target}"
        converters[sec] = conv

    return converters


def apply_converters(path, converters, default_suffix):
    suffixes = [""]
    if default_suffix is not None:
        suffixes.append(default_suffix)

    for name, conv in converters.items():
        for suffix in suffixes:
            target_path =  path + "." + suffix
            m = conv["target"].match(target_path)
            if m is not None:
                break
        if m is None:
            continue

        src = conv["target"].sub(conv["source"], target_path)

        if not os.path.exists(src):
            continue

        message = conv["message"].format(source=src, target=target_path)
        message += " [%s]" % name
        print(message)

        PATH = os.getenv("PATH", "")
        if len(PATH) > 0:
            PATH = ":" + PATH
        PATH = BIN_PATH + PATH

        command = [c.format(source=src, target=target_path)
                   for c in conv["command"]]
        subprocess.check_call(command, env={"PATH": PATH})
        break


def main(argv):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Default converters are specified in %(rules)s. Additional rules can override
existing ones.
        """ % {"rules": DEFAULT_RULES})

    parser.add_argument("log", help="Compilation log for TeX document",
                        type=file)
    parser.add_argument("--rules", action="append", default=[DEFAULT_RULES],
                        type=file,
                        help="Additional rules file")
    parser.add_argument("--suffix",
                        help="Implicit suffix for target files")

    args = parser.parse_args(argv)

    log = args.log.name
    missing = log_get_missing(log)

    if len(missing) == 0:
        return

    converters = search_converters(args.rules)

    for path in missing:
        apply_converters(path, converters, args.suffix)


if __name__ == "__main__":
    main(sys.argv[1:])
