# clipssh · 远程截图传输预览

这是基于 [samuellawrentz/clipssh](https://github.com/samuellawrentz/clipssh) 的社区 fork，保留原作者署名和 MIT 许可证。它把本机剪贴板里的截图通过 SSH 传到远端，并复制远端路径，方便交给远程运行的 Claude Code、Codex 等工具。

这个预览版为每次上传创建独立的私有目录，避免两次上传使用同一个秒级文件名。它不是原项目的官方发行版。

## 安装

macOS 先安装截图读取工具：

```bash
brew install pngpaste
git clone --branch fix/unique-remote-upload https://github.com/LydiaTools/clipssh.git
cd clipssh
./install.sh
```

Linux 需要 `xclip` 或 `wl-clipboard`。安装脚本须在克隆后的目录中运行；它安装的是当前目录里的预览版。

## 使用

1. 将截图复制到本机剪贴板。
2. 运行 `clipssh user@host`；也可以使用已有的 SSH 配置别名。
3. 粘贴已复制的远端路径，让远程工具读取图片。

默认在远端 `/tmp` 下创建 `clipboard-<随机字符>/image.png`；如需其他位置，可在运行前设置 `CLIPSSH_REMOTE_DIR`，该目录须已存在。私有目录权限为 `0700`，图片为 `0600`。不再需要时，请在远端删除图片和它的目录。

如果传输中 SSH 断开，上传结果可能未知；重试前可检查远端目录。原始图片和远端文件由你管理，工具不会自动清理已完成的上传。

## 验证范围

本次在 macOS 使用合成图片、剪贴板替身和临时本机 SSH 服务，验证了并发上传生成不同路径、文件内容一致和权限；还测试了传输失败及异常响应。GitHub 自动检查在 Linux 和 macOS 上运行模拟测试。**尚未测试真实剪贴板、外部 SSH 服务器或 Windows。**

在源码目录运行 `python3 -m unittest discover -s tests -v` 可执行本地模拟测试；其中 SSH 和剪贴板均为替身。本机回环 SSH 检查不包含在仓库测试中。

[English](README.md) · [原项目](https://github.com/samuellawrentz/clipssh) · [许可证](LICENSE)
