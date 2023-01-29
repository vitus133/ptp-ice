#!/bin/bash
config=$(ps -ef |grep "/usr/sbin/phc2sys" |grep ? |cut -d '[' -f 2 |cut -d ']' -f 1)
pid=$(ps -ef |grep /usr/sbin/ptp4l |grep $config |tr -s " " |cut -d " " -f 2)

echo "pid $pid, config $config"

echo 0 > /sys/kernel/debug/tracing/tracing_on
echo > /sys/kernel/debug/tracing/trace
echo 0 > /sys/kernel/debug/tracing/events/irq/enable
echo 0 > /sys/kernel/debug/tracing/events/sched/enable
echo 0 > /sys/kernel/debug/tracing/events/sched/sched_switch/enable
echo 0 > /sys/kernel/debug/tracing/events/sched/sched_wakeup/enable
echo $pid > /sys/kernel/debug/tracing/set_event_pid
echo 1 > /sys/kernel/debug/tracing/events/syscalls/sys_enter_poll/enable
echo 1 > /sys/kernel/debug/tracing/events/syscalls/sys_exit_poll/enable
echo 1 > /sys/kernel/debug/tracing/tracing_on