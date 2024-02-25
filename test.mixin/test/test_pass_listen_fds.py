#!/usr/bin/env python3

import os
import sys
from socket import *
from stat import S_ISSOCK

LISTEN_FDS_START = 3
LISTEN_FDS = os.getenv("LISTEN_FDS")
LISTEN_PID = os.getenv("LISTEN_PID")
LISTEN_FDNAMES = os.getenv("LISTEN_FDNAMES")


def expect_four():
    global LISTEN_FDS_START
    global LISTEN_FDS
    global LISTEN_PID
    global LISTEN_FDNAMES

    LISTEN_FDS = int(LISTEN_FDS)
    LISTEN_PID = int(LISTEN_PID)

    # Check LISTEN_FDS env var
    assert LISTEN_FDS == 4, f"LISTEN_FDS={LISTEN_FDS}"

    # Check passed file descriptors
    fds = [LISTEN_FDS_START + n for n in range(LISTEN_FDS)]
    for fd in fds:
        # Expect FDs to be sockets
        mode = os.stat(fd).st_mode
        assert S_ISSOCK(mode), f"fd={fd} mode={mode:#o}"

        # Check socket domain, type, proto, and address
        sd = socket(fileno=fd)
        domain = sd.getsockopt(SOL_SOCKET, SO_DOMAIN)
        type_ = sd.getsockopt(SOL_SOCKET, SO_TYPE)
        proto = sd.getsockopt(SOL_SOCKET, SO_PROTOCOL)
        laddr = sd.getsockname()

        # print(f"domain={domain} type={type_} proto={proto} laddr={laddr}")

        match fd:
            case 3:
                assert (
                    domain == AF_INET
                    and type_ == SOCK_STREAM
                    and proto == IPPROTO_TCP
                    and laddr[0] == "127.0.0.1"
                    and laddr[1] in (1111, 2222)
                )
            case 4:
                assert (
                    domain == AF_INET6
                    and type_ == SOCK_STREAM
                    and proto == IPPROTO_TCP
                    and laddr[0] == "::1"
                    and laddr[1] in (1111, 2222)
                )
            case 5:
                assert (
                    domain == AF_INET
                    and type_ == SOCK_DGRAM
                    and proto == IPPROTO_UDP
                    and laddr[0] == "127.0.0.1"
                    and laddr[1] in (1111, 2222)
                )
            case 6:
                assert (
                    domain == AF_INET6
                    and type_ == SOCK_DGRAM
                    and proto == IPPROTO_UDP
                    and laddr[0] == "::1"
                    and laddr[1] in (1111, 2222)
                )

    # Check LISTEN_PID env var
    assert LISTEN_PID == os.getpid(), f"LISTEN_PID={LISTEN_PID}"

    # Check LISTEN_FDNAMES env var
    fdnames_str = ":".join(["test"] * LISTEN_FDS)
    assert LISTEN_FDNAMES == fdnames_str, f"LISTEN_FDNAMES={LISTEN_FDNAMES}"


def expect_none():
    global LISTEN_FDS
    global LISTEN_PID
    global LISTEN_FDNAMES

    assert LISTEN_FDS is None
    assert LISTEN_PID is None
    assert LISTEN_FDNAMES is None


def main():
    args = iter(sys.argv)
    arg0 = next(args)
    arg1 = next(args, "")
    arg2 = next(args, "")

    match (arg1, arg2):
        case ("expect", "four"):
            expect_four()
        case ("expect", "none"):
            expect_none()
        case _:
            prog_name = os.path.basename(arg0)
            print(f"usage: {prog_name} expect {{ four | none }}")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
