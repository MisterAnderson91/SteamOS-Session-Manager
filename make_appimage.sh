#!/bin/bash
set -e

APP_NAME="session_manager"
APP_TITLE="SteamOS Session Manager"

echo "=== 1. Setting up Python Virtual Environment ==="
# Use a venv to avoid messing with system packages and bypass pip lock restrictions
python3 -m venv build_env
source build_env/bin/activate

echo "=== 2. Installing Dependencies ==="
pip install --upgrade pip
pip install PyQt6 pyinstaller

echo "=== 3. Bundling App with PyInstaller ==="
# --noconsole prevents a terminal window from popping up behind the GUI
pyinstaller --noconfirm --noconsole --onedir "${APP_NAME}.py"

echo "=== 4. Setting up AppDir Structure ==="
rm -rf AppDir
mkdir -p AppDir/usr/bin

# Copy the bundled python app into the AppDir
cp -r dist/${APP_NAME}/* AppDir/usr/bin/

echo "=== 5. Creating AppRun and Desktop Integration ==="
# Create the AppRun entry point
cat > AppDir/AppRun << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/session_manager" "$@"
EOF
chmod +x AppDir/AppRun

# Create the .desktop file required by AppImage
cat > AppDir/${APP_NAME}.desktop << EOF
[Desktop Entry]
Type=Application
Name=${APP_TITLE}
Exec=${APP_NAME}
Icon=${APP_NAME}
Categories=Utility;
EOF

# Create a transparent 1x1 dummy icon (AppImages require an icon file to build successfully)
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==" | base64 -d > AppDir/${APP_NAME}.png

echo "=== 6. Downloading AppImageTool ==="
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    wget -q --show-progress -O appimagetool-x86_64.AppImage https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
fi

# Ensure it is executable whether it was just downloaded or already existed
chmod +x appimagetool-x86_64.AppImage

echo "=== 7. Packaging into .AppImage ==="
# Run appimagetool (we use --appimage-extract-and-run to avoid FUSE mount issues on some Linux setups)
./appimagetool-x86_64.AppImage --appimage-extract-and-run AppDir SteamOS_Session_Manager-x86_64.AppImage

echo "=== 8. Cleaning up build files ==="
deactivate
rm -rf build_env build dist AppDir ${APP_NAME}.spec

echo "=== Done! ==="
echo "Your portable app is ready: SteamOS_Session_Manager-x86_64.AppImage"
