Playground for passing listen FDs to socket unit `Exec*=` commands.

<https://github.com/systemd/systemd/issues/6714>

Demo:

```
$ just boot
…
Fedora Linux 39 (Thirty Nine)
Kernel 6.7.4-200.fc39.x86_64 on an x86_64 (pts/0)

pass-fds-to-exec login: root (automatic login)

● socket-dispatch.service - Sample socket dispatch service using BPF sk_lookup program
     Loaded: loaded (/etc/systemd/system/socket-dispatch.service; static)
    Drop-In: /usr/lib/systemd/system/service.d
             └─10-timeout-abort.conf
     Active: active (exited) since Sun 2024-02-25 22:33:34 CET; 147ms ago
    Process: 82 ExecStartPre=/sbin/bpftool --nomount prog loadall /example/socket_dispatch.bpf.o /sys/fs/bpf/socket-dispatch pinmaps /sys/fs/bpf/socket-dispatch (code=exited, status=0/SUCCESS)
    Process: 85 ExecStartPre=/sbin/bpftool --nomount map update pinned /sys/fs/bpf/socket-dispatch/port_service_map key hex 07 00 value hex 64 61 79 74 69 6d 65 00 (code=exited, status=0/SUCCESS)
    Process: 88 ExecStart=/example/sk_lookup_attach.py /sys/fs/bpf/socket-dispatch/socket_dispatch_prog /sys/fs/bpf/socket-dispatch/socket_dispatch_link (code=exited, status=0/SUCCESS)
   Main PID: 88 (code=exited, status=0/SUCCESS)

Feb 25 22:33:34 pass-fds-to-exec systemd[1]: Starting socket-dispatch.service...
Feb 25 22:33:34 pass-fds-to-exec systemd[1]: Finished socket-dispatch.service.
● daytime.socket - Daytime service socket
     Loaded: loaded (/etc/systemd/system/daytime.socket; enabled; preset: disabled)
     Active: active (listening) since Sun 2024-02-25 22:33:34 CET; 8ms ago
     Listen: 127.0.0.1:12345 (Stream)
   Accepted: 0; Connected: 0;
    Process: 122 ExecStartPost=/example/sockhash_update.py /sys/fs/bpf/socket-dispatch/service_socket_map daytime (code=exited, status=0/SUCCESS)
      Tasks: 0 (limit: 38122)
     Memory: 28.0K (peak: 5.6M)
        CPU: 26ms
     CGroup: /system.slice/daytime.socket

Feb 25 22:33:34 pass-fds-to-exec systemd[1]: Starting daytime.socket...
Feb 25 22:33:34 pass-fds-to-exec systemd[1]: Listening on daytime.socket.
[root@pass-fds-to-exec ~]# nc 127.1.1.1 7 < /dev/null
Sun Feb 25 22:34:05 CET 2024
[root@pass-fds-to-exec ~]#
```
