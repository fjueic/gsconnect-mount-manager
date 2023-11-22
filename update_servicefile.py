#!/usr/bin/env python

import sys

args = sys.argv
home = args[1]
script_dir = args[2]


def update_servicefile():
    with open(f"{script_dir}/gsconnect-mount-manager.service", "r+") as f:
        data = f.read()
        data = data.replace("{HOME}", home)
        return data


if __name__ == "__main__":
    print(update_servicefile())
