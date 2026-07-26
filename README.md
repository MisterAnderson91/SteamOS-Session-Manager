# SteamOS Session Manager

[![Build AppImage](https://github.com/MisterAnderson91/SteamOS-Session-Manager/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/MisterAnderson91/SteamOS-Session-Manager/actions)

A lightweight GUI for SteamOS to manage your default boot state (Game Mode vs. Desktop Mode) using native `steamosctl` commands.

## Features
* **Set Boot Mode:** Boot directly to Game Mode or Desktop Mode on startup.
* **Current Status:** Displays your currently configured boot mode.

## Usage
1. Download the latest `.AppImage` from the [Releases page](https://github.com/MisterAnderson91/SteamOS-Session-Manager/releases).
2. Right-click the file, check **Is executable** in Properties (or use `chmod +x`), and double-click to run.

## Building from Source
Python 3 is required. The included script sets up an isolated environment and builds the AppImage automatically.

```bash
git clone https://github.com/MisterAnderson91/SteamOS-Session-Manager.git
cd SteamOS-Session-Manager
chmod +x make-appimage.sh
./make-appimage.sh
```

## Manual Session Selection
If you wish to change the current session on SteamOS without downloading this app, use the commands below in Konsole in Desktop Mode:

Boot into Game Mode:
```bash
steamosctl set-default-login-mode game
```

Boot into Desktop Mode:
```bash
steamosctl set-default-login-mode desktop
```
    
Check the current setting:
```bash
steamosctl get-default-login-mode
```

## License
This project is licensed under the [GNU General Public License v3.0 (GPLv3)](LICENSE).
