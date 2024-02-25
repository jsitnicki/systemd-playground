#!/usr/bin/python3
#
# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Cloudflare, Inc.
#

from argparse import ArgumentParser
from functools import cached_property
from os import getenv, stat
from stat import S_ISSOCK
from ctypes import *

from bpf import *

LISTEN_FDS_START = 3
MAP_KEY_LEN = 8


def main():
    args = parse_args()

    map_path = c_char_p(args.map_path.encode("utf-8"))
    elem_key = args.elem_key.encode("ascii")

    assert len(elem_key) <= MAP_KEY_LEN, f"elem_key too long, max {MAP_KEY_LEN} chars"

    obj_get = BpfObjGetAttr()
    obj_get.pathname = cast(map_path, c_void_p).value
    obj_get.file_flags = BPF_F_WRONLY

    map_fd = bpf(BPF_OBJ_GET, obj_get)
    assert map_fd != -1, "bpf(OBJ_GET) failed"

    listen_fds = getenv("LISTEN_FDS", "0")
    assert int(listen_fds) == 1, "too many LISTEN_FDS"

    sock_fd = LISTEN_FDS_START
    assert S_ISSOCK(stat(sock_fd).st_mode), "passed FD is not a socket"

    key = create_string_buffer(elem_key, MAP_KEY_LEN)
    value = c_uint64(sock_fd)

    map_update_elem = BpfMapUpdateElemAttr()
    map_update_elem.map_fd = map_fd
    map_update_elem.key = cast(byref(key), c_void_p).value
    map_update_elem.value = cast(byref(value), c_void_p).value
    map_update_elem.flags = BPF_ANY

    ret = bpf(BPF_MAP_UPDATE_ELEM, map_update_elem)
    assert ret == 0, "bpf(MAP_UPDATE_ELEM) failed"


def parse_args():
    parser = ArgumentParser(
        description="Insert socket FD inherited via sd_listen_fds into BPF sockhash map."
    )
    parser.add_argument("map_path", help="where to find pinned BPF sockhash map")
    parser.add_argument(
        "elem_key",
        help=f"string to use as key into BPF map (max {MAP_KEY_LEN} chars)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
