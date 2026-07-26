# SteamOS Session Manager

[![Build AppImage](https://github.com/MisterAnderson91/SteamOS-Session-Manager/actions/workflows/build.yml/badge.svg)](https://github.com/MisterAnderson91/SteamOS-Session-Manager/actions)

A lightweight GUI for SteamOS to manage your default boot state (Game Mode vs. Desktop Mode) using native `steamosctl` commands.

## Features
* **Set Boot Mode:** Boot directly to Game Mode or Desktop Mode on startup.
* **Live Status:** Displays your currently configured boot mode.
* **X11 Reset:** Detects X11 desktop sessions and offers a 1-click reset to the default Wayland session (`plasma.desktop`).
* **Portable:** Distributed as a single `.AppImage` executable.

## Usage
1. Download the latest `.AppImage` from the [Releases page](https://github.com/MisterAnderson91/SteamOS-Session-Manager/releases).
2. Right-click the file, check **Is executable** in Properties (or use `chmod +x`), and double-click to run.

## Building from Source
Python 3 is required. The included script sets up an isolated environment and builds the AppImage automatically.

    git clone https://github.com/MisterAnderson91/SteamOS-Session-Manager.git
    cd SteamOS-Session-Manager
    chmod +x make-appimage.sh
    ./make-appimage.sh

## License
This project is licensed under the [GNU General Public License v3.0 (GPLv3)](LICENSE).
