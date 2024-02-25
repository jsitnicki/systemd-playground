#!/usr/bin/python3
#
# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Cloudflare, Inc.
#

from argparse import ArgumentParser
from ctypes import *

from bpf import *


def main():
    args = parse_args()

    prog_path = c_char_p(args.prog_path.encode("utf-8"))
    link_path = c_char_p(args.link_path.encode("utf-8"))

    obj_get = BpfObjGetAttr()
    obj_get.pathname = cast(prog_path, c_void_p).value
    obj_get.file_flags = BPF_F_RDONLY

    prog_fd = bpf(BPF_OBJ_GET, obj_get)
    assert prog_fd != -1

    netns = open("/proc/self/ns/net")

    link_create = BpfLinkCreateAttr()
    link_create.prog_fd = prog_fd
    link_create.target_fd = netns.fileno()
    link_create.attach_type = BPF_SK_LOOKUP

    link_fd = bpf(BPF_LINK_CREATE, link_create)
    assert link_fd != -1

    obj_pin = BpfObjPinAttr()
    obj_pin.pathname = cast(link_path, c_void_p).value
    obj_pin.bpf_fd = link_fd

    ret = bpf(BPF_OBJ_PIN, obj_pin)
    assert ret == 0


def parse_args():
    parser = ArgumentParser(
        description="Attach BPF sk_lookup program to current network namespace."
    )
    parser.add_argument("prog_path", help="where to find pinned BPF sk_lookup program")
    parser.add_argument("link_path", help="where to pin BPF link for attached program")
    return parser.parse_args()


if __name__ == "__main__":
    main()
