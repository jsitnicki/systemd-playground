# coding: utf-8
#
# SPDX-License-Identifier: MIT
# Copyright (c) 2024 Cloudflare, Inc.
#

"""
Incomplete bindings for linux/bpf.h
"""

from ctypes import *

# Commands

BPF_MAP_UPDATE_ELEM = 2
BPF_OBJ_PIN = 6
BPF_OBJ_GET = 7
BPF_LINK_CREATE = 28

# Flags

BPF_F_RDONLY = 1 << 3
BPF_F_WRONLY = 1 << 4

BPF_ANY = 0

# Attach types
BPF_SK_LOOKUP = 36

# Attributes


class BpfAttr(Structure):
    def __init__(self):
        # can't specify minimum alignment with ctypes
        assert addressof(self) % 8 == 0
        # does ctypes guarantee zeroed memory?
        memset(byref(self), 0, sizeof(self))


class BpfMapUpdateElemAttr(BpfAttr):
    _fields_ = [
        ("map_fd", c_uint32),
        ("key", c_uint64),
        ("value", c_uint64),
        ("flags", c_uint64),
    ]


class BpfObjGetAttr(BpfAttr):
    _fields_ = [
        ("pathname", c_uint64),
        ("bpf_fd", c_uint32),
        ("file_flags", c_uint32),
        ("path_fd", c_int32),
    ]


class BpfObjPinAttr(BpfObjGetAttr):
    pass


class BpfLinkCreateAttr(BpfAttr):
    _fields_ = [
        ("prog_fd", c_uint32),
        ("target_fd", c_uint32),
        ("attach_type", c_uint32),
        ("flags", c_uint32),
    ]


# Syscall

_libc = CDLL(None)
_syscall = _libc.syscall


def bpf(cmd, attr):
    SYS_bpf = 321  # x86-64, 64-bit ABI
    return _syscall(SYS_bpf, cmd, byref(attr), sizeof(attr))
