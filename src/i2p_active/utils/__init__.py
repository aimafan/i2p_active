def ADD_SYS_PATH():
    # 将模块添加到sys.path
    import sys
    import os

    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 计算出 util 所在的目录
    util_dir = os.path.join(current_dir, '..',)

    # 将 util 所在的目录添加到 sys.path
    sys.path.append(util_dir)
    #