#!/bin/bash
# 将项目代码上传到vps1

# 获取脚本文件的完整路径
script_path=$(realpath "$0")

# 获取脚本所在的目录
script_dir=$(dirname "$script_path")


cd $script_dir/../../

tar cf i2p_active.tar --exclude="i2p_active/.venv" --exclude="i2p_active/.git" i2p_active

REMOTE_SERVER=vps1
scp i2p_active.tar $REMOTE_SERVER:~/

COMMAND="rm -rf i2p_active; tar xf i2p_active.tar"


# 使用 SSH 执行远程命令
ssh ${REMOTE_SERVER} "${COMMAND}"