# clipssh

> **LydiaTools community fork — collision fix preview.** Based on [samuellawrentz/clipssh](https://github.com/samuellawrentz/clipssh), with its MIT license and authorship retained. This branch gives each upload a private, unique remote directory to avoid reusing a filename. Tested on macOS with synthetic clipboard inputs and a temporary loopback SSH server; Linux, Windows, real clipboards, and external SSH hosts have not been tested here. This fork is not an upstream release.

Send clipboard screenshots to remote SSH hosts. Perfect for pasting images into AI coding tools like Claude Code or OpenCode running over SSH.

## The Problem

When using Claude Code, OpenCode (or similar tools) over SSH, you can't paste images from your local clipboard. The remote terminal has no access to your local display server.

## The Solution

`clipssh` extracts the screenshot from your local clipboard, uploads it to the remote server, and copies the file path to your clipboard. Just paste the path into Claude Code, OpenCode, or any terminal tool and it auto-attaches the image.

## Install

```bash
# macOS: install the clipboard dependency first
brew install pngpaste

# Clone this preview fork, then install from the checkout
git clone --branch fix/unique-remote-upload https://github.com/LydiaTools/clipssh.git
cd clipssh
./install.sh
```

On Linux, install `xclip` or `wl-clipboard` before running the installer. The installer must run from this checkout; it does not download the original upstream version.

## Usage

```bash
# 1. Take a screenshot to the clipboard
# macOS: Cmd+Shift+Ctrl+4 (select area, copies to clipboard)

# 2. Run the clipssh command to move the clipboard file to the SSH machine
clipssh user@myserver

# 3. Cmd/Ctrl + V in SSH Machine
# The image will auto-attach
```

## Custom SSH Port

Specify a custom SSH port directly in the host target using the `user@host:port` format:

```bash
clipssh user@myserver.com:2222
```

This syntax is also fully supported in aliases and default host environment variables:

```bash
# Save an alias with a custom port
clipssh alias add myserver user@myserver.com:2222

# Or configure it as default
export CLIPSSH_HOST=user@myserver.com:2222
```

### Alternative: SSH Configuration (`~/.ssh/config`)

Since `clipssh` delegates connections directly to your system's standard `ssh` client, it seamlessly obeys any configurations defined in your local `~/.ssh/config` file. This is often the cleanest way to manage custom ports, private keys, or proxy jumps.

Example config block:
```ssh
Host myserver
    HostName myserver.example.com
    User user
    Port 2222
```

Once defined in your SSH config, you can simply run:
```bash
clipssh myserver
```

## Aliases

Save hosts under short names so you don't have to type `user@host` every time.

```bash
# Save an alias
clipssh alias add myserver user@myserver.com

# List saved aliases
clipssh alias list

# Remove an alias
clipssh alias remove myserver

# Use an alias directly
clipssh myserver
```

Aliases are stored in `~/.clipssh/aliases`, one `name=user@host` per line.

## Set Default Host

```bash
# Add to ~/.zshrc or ~/.bashrc
export CLIPSSH_HOST=user@myserver

# Now just run:
clipssh
```

`CLIPSSH_HOST` also accepts an alias name.

## Change Upload Directory

Uploads land in `/tmp` by default. Override with `CLIPSSH_REMOTE_DIR`:

```bash
export CLIPSSH_REMOTE_DIR=~/.cache/clipssh   # must already exist on the remote
```

Each upload is placed in a newly created private directory under the chosen remote directory. Files use `0600` and directories use `0700`; simultaneous uploads do not reuse a timestamp-based filename. Remove the uploaded file and its containing directory on the remote when they are no longer needed. If SSH disconnects during upload, the outcome may be unknown; check the remote directory before retrying.

## Requirements

**macOS:**
- `pngpaste` - Install with `brew install pngpaste`
- SSH access to remote host

**Linux:**
- `xclip` (X11) or `wl-clipboard` (Wayland)
- SSH access to remote host

## How It Works

1. Extracts PNG image from your local clipboard
2. Creates `$CLIPSSH_REMOTE_DIR/clipboard-<random>/image.png` (default `/tmp`) on the remote host via SSH, with a private directory and `0600` file
3. Copies the remote path to your clipboard
4. You paste the path into Claude Code, OpenCode, or any tool, which reads and displays the image

## License

MIT
