#!/usr/bin/env bash

# 推送flowlog数据

# 获取脚本文件的完整路径
script_path=$(realpath "$0")

# 获取脚本所在的目录
script_dir=$(dirname "$script_path")


cd $script_dir/../src/i2p_active

python3 -m active.action2

cd -