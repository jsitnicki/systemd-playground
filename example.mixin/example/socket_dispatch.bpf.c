// SPDX-License-Identifier: (GPL-2.0-only OR BSD-2-Clause)
/* Copyright (c) 2024 Cloudflare, Inc. */

#include <linux/bpf.h>
#include <linux/types.h>

#include <bpf/bpf_helpers.h>

#define _cleanup_(f) __attribute__((cleanup(f)))

enum {
	NAME_LEN = 8,
	MAX_PORTS = 1 << 16,
};

struct service {
	char name[NAME_LEN];
};

struct {
	__uint(type, BPF_MAP_TYPE_HASH);
	__type(key, __u16);
	__type(value, struct service);
	__uint(max_entries, MAX_PORTS);
} port_service_map SEC(".maps");

struct {
	__uint(type, BPF_MAP_TYPE_SOCKHASH);
	__type(key, struct service);
	__type(value, __u64);
	__uint(max_entries, MAX_PORTS);
} service_socket_map SEC(".maps");

int last_errno;

static __always_inline void bpf_sk_release_p(struct bpf_sock **p)
{
	if (p && *p)
		bpf_sk_release(*p);
}

SEC("sk_lookup")
int socket_dispatch_prog(struct bpf_sk_lookup *ctx)
{
	_cleanup_(bpf_sk_release_p) struct bpf_sock *socket = NULL;
	struct service *service = NULL;
	__u16 local_port;
	int err;

	last_errno = 0;

	local_port = ctx->local_port;
	service = bpf_map_lookup_elem(&port_service_map, &local_port);
	if (!service)
		return SK_PASS;	/* port not mapped to any service */

	socket = bpf_map_lookup_elem(&service_socket_map, service);
	if (!socket)
		return SK_DROP;	/* port mapped to service but socket missing */

	err = bpf_sk_assign(ctx, socket, /* flags= */ 0);
	if (!err)
		return SK_PASS;	/* redirect packet to service socket */

	last_errno = -err;
	return SK_DROP;	/* socket rejected, not compatible with packet */
}

SEC("license") const char __license[] = "Dual BSD/GPL";
