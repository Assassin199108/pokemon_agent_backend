# LINUX
## 给apt换源
```
cd /etc/apt/

# 留个source备份
sudo mv sources.list sources.list.backup

# 使用源
sudo vim sources.list
```
写入：（根据ubuntu版本号自己查，如果源的版本和ubuntu版本不一致，那么后续更新就会发生依赖问题。e.g. Ubuntu20.04对应focal-XXX的源）
```
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse

deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse multiverse
```

移除自带的包（因为可能和国内源的软件有冲突）
```
sudo apt remove ubuntu-advantage-tools
```
更新一下

```
sudo apt update
sudo apt upgrade
```
## 安装基本开发工具
```
# mingw套组
sudo apt install build-essential cmake 

# python3 pip 工具
sudo apt install python3-pip
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```
## 美化终端（使用zsh）
安装
```
sudo apt install zsh
chsh -s $(which zsh)
```
在bashrc里面加入
```
export SHELL=`which zsh`
[ -z "$ZSH_VERSION" ] && exec "$SHELL" -l
```
重新打开当前终端，就会进入zsh终端，接着安装oh-my-zsh主题框架。
```
cd ~
git clone https://gitee.com/mirrors/oh-my-zsh
sh oh-my-zsh/tools/install.sh
```

安装两个插件
```
cd ~/.oh-my-zsh/custom/plugins/

# 高亮关键词
git clone https://gitee.com/testbook/zsh-syntax-highlighting.git

# 自动补全
git clone https://gitee.com/qiushaocloud/zsh-autosuggestions

# 更加丰富的高亮
git clone https://gitee.com/wangl-cc/fast-syntax-highlighting

# 展示自动补全历史
git clone https://gitee.com/wenhuifu/zsh-autocomplete
```
然后进入~/.zshrc在plugins参数中添加zsh-syntax-highlighting和zsh-autosuggestions。也就是说你的.zshrc中必须要有一行长这样：
```
plugins=(git zsh-syntax-highlighting zsh-autosuggestions fast-syntax-highlighting zsh-autocomplete)

主题设置
ZSH_THEME="ys"
```
## 安装部分驱动程序
默认pip 版本较低，升级一下
```
pip install --upgrade pip
```
安装opencv的包
```
sudo apt install libopencv-dev
pip install opencv-python
```
安装torch cuda
```
sudo apt install nvidia-cuda-toolkit
然后去https://pytorch.org/找对应的安装指令。
```