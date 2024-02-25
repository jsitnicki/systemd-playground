home_dir := env_var("HOME")
this_dir := justfile_directory()

sd_build_dir := home_dir + "/src/systemd/build"
sd_stage_dir := this_dir + "/systemd.stage"

os_base_dir := this_dir + "/basefs"
os_conf_dir := this_dir + "/config.mixin"
os_test_dir := this_dir + "/test.mixin"
os_example_dir := this_dir + "/example.mixin"

help:
	@just --list

build-basefs:
	mkosi -f -d fedora \
	-p bpftool \
	-p iproute \
	-p less \
	-p lsof \
	-p nmap-ncat \
	-p python3 \
	-p strace \
	-p udev \
	-p util-linux \
	-t directory \
	-O $(dirname {{ os_base_dir }}) -o $(basename {{ os_base_dir }}) \
	build

build-systemd:
	ninja -C {{ sd_build_dir }}
	DESTDIR={{ sd_stage_dir }} meson install -C {{ sd_build_dir }}

boot:
	sudo \
	systemd-nspawn \
	--boot \
	--machine=pass-fds-to-exec \
	--capability=cap_bpf,cap_net_admin \
	--system-call-filter=bpf \
	--directory={{ os_base_dir }} \
	--overlay=+/:{{ os_conf_dir }}:{{ os_test_dir }}:{{ sd_stage_dir }}:{{ os_example_dir }}::/
