# 初始化项目
# 配置powershell
```
# 允许运行Install-Module脚本
set-executionpolicy remotesigned
# 检查当前执行策略
get-ExecutionPolicy -List

# 更新最新版本的PSReadLine，为了自动补全
Install-Module PSReadLine -Force

# 安装几个插件
Install-Module posh-git
Install-Module Terminal-Icons
```
# 美化shell
1. 微软应用商店搜索安装 Windows Terminal
2. 进行相关设置：
打开JSON设置，定位到Defaults里添加 效果
3. 安装oh-my-posh
```
winget 微软商店搜索"应用安装程序" 更新
winget install oh-my-posh
修改启动脚本
code $PROFILE/ notepad $PROFILE
输入：
oh-my-posh init pwsh --config $env:POSH_THEMES_PATH\montys.omp.json | Invoke-Expression
Import-Module posh-git
Import-Module Terminal-Icons
Set-PSReadLineOption -PredictionSource History
Set-PSReadlineKeyHandler -Key Tab -Function MenuComplete
cls

解决字体乱码，安装Nerd字体
推荐：
JetBrains Mono Medium Nerd Font Complete Mono
下载地址 https://www.nerdfonts.com/font-downloads

修改字体 在default下 
key为fontFace -- 字体类型
key为fontSize -- 字体大小
```
# 安装WSL2
以管理员身份打开windows terminal
```
# 开启VM组件 开启后需要重启电脑
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

# 安装Ubuntu
wsl --install -d Ubuntu

# 设置为wsl2
wsl --set-default-version 2

wsl常见命令
列出已安装的Linux发行版
 wsl -l -v
导出/备份
 wsl --export Ubuntu Ubuntu.tar
导入/还原/利用备份创建新的镜像
 wsl --import Anaconda <URL>
启动指定的镜像
 wsl -d Ubuntu --user <UserName>
关闭指定的镜像
 wsl --terminate Ubuntu
删除指定的镜像
 wsl --unregister Ubuntu
```

# 下载Git
前往 https://git-scm.com/download/win
## 配置信息：
```
git config --global user.email xxx
git config --global user.name xxx
```
## 设置代理
```
 git config --global http.proxy http://127.0.0.1:<端口号>
 git config --global https.proxy https://127.0.0.1:<端口号>
```
## 设置环境变量
我的电脑-属性-高级系统设置-环境变量-path-编辑-新建-浏览
## git 验证
power shell验证

# Miniconda安装及使用
```
介绍：Miniconda 是一个轻量级的 Conda 发行版，它提供了 Conda 包管理和虚拟环境管理功能，但只包含了 Python 和 conda 及其依赖项，而不像 Anaconda 那样预装了大量的科学计算、数据分析和机器学习相关的包。因此，Miniconda 更适合那些希望从零开始构建自己所需环境的用户，或者只需要特定软件包的用户。
下载地址：https://mirror.tuna.tsinghua.edu.cn/
https://mirror.tuna.tsinghua.edu.cn/anaconda/miniconda/

```

# 安装python
1. 去 https://www.python.org/downloads/windows/ 寻找稳定版本的x64可执行文件下载
2. 配置pip源：
```
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple --user
pip config set global.proxy http://127.0.0.1:<端口号> --user
```
# 安装nvm
node 包管理工具
下载NVM for Windows
https://github.com/coreybutler/nvm-windows/releases
```
nvm-noinstall.zip： 这个是绿色免安装版本，但是使用之前需要配置

nvm-setup.zip：这是一个安装包，下载之后点击安装，无需配置就可以使用，方便。
```

# 安装Node
1. 安装node https://nodejs.org/en/download/
2. npm 换源
```
npm config set registry https://registry.npmmirror.com
```
# 安装java
安装地址：https://www.oracle.com/hk/java/technologies/downloads/

# 安装MinGW
https://sourceforge.net/projects/mingw/
忘记安装配置怎么选看:<a>https://blog.csdn.net/QuantumYou/article/details/119676283</a>

# 安装gemini-cli
```
1. 安装gemini-cli npm -g install @google/gemini-cli
2. 配置API Key，环境变量 新建变量名 GEMINI_API_KEY 输入API KEY
3. 启动 gemini
```

python包管理: uv
交互式代码执行环境： Jupyter Notebook
# 通关uv初始化项目
放弃--windows没有办法




参考： https://kirigaya.cn/blog/article?seq=28 windows电脑配置开发流程