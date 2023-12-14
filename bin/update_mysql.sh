#!/bin/bash
# 在vps1上执行对i2p的主动探测任务

# 获取脚本文件的完整路径
script_path=$(realpath "$0")

# 获取脚本所在的目录
script_dir=$(dirname "$script_path")


cd $script_dir/../src/i2p_active

python -m mysql_handle.mysql

REMOTE_SERVER=vps1

scp $script_dir/../data/output.csv vps1:~/i2p_active/data/

# # 在远程服务器上执行的命令或脚本
# COMMAND="bash ~/i2p_active/bin/i2p.sh"

# # 使用 SSH 执行远程命令
# ssh ${REMOTE_SERVER} "${COMMAND}"