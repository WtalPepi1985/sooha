#!/usr/bin/env bash
# Builds SOOHA_vX.Y.Z.exe via Wine on LXC 123 (wine-builder, 10.10.4.179)
set -euo pipefail

CONTAINER=123
BUILD_DIR=/opt/sooha-build
WINEPREFIX=/opt/wine-python
PYINSTALLER="C:\\\\Python311\\\\Scripts\\\\pyinstaller.exe"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SOURCES=(main.py mqtt_client.py screen.py sensors.py ha_client.py config.py settings.py version.py)
ASSETS=(assets/Systemtrayicon.png assets/Programmicon.png assets/icon.ico)

# ── Version aus version.py lesen ─────────────────────────────────────────────
VERSION=$(python3 -c "import re; print(re.search(r'\"(.+?)\"', open('$SCRIPT_DIR/version.py').read()).group(1))")
EXE_NAME="SOOHA_v${VERSION}"
EXE_FILE="${EXE_NAME}.exe"

# ── Parse args ────────────────────────────────────────────────────────────────
UPDATE_DEPS=0
for arg in "$@"; do
  case "$arg" in
    --update-deps) UPDATE_DEPS=1 ;;
    --help|-h)
      echo "Usage: $0 [--update-deps]"
      echo "  --update-deps   Reinstall pip packages before building"
      exit 0 ;;
  esac
done

pct() { ssh proxmox "pct $*"; }

# ── Sanity check ──────────────────────────────────────────────────────────────
echo "[1/4] Checking wine-builder (v${VERSION})..."
STATUS=$(pct status $CONTAINER 2>&1)
if [[ "$STATUS" != *"running"* ]]; then
  echo "  Container $CONTAINER is not running — starting..."
  pct start $CONTAINER
  sleep 3
fi
echo "  OK"

# ── Copy sources ──────────────────────────────────────────────────────────────
echo "[2/4] Copying source files..."
ssh proxmox "pct exec $CONTAINER -- bash -c 'mkdir -p $BUILD_DIR/assets'"
for f in "${SOURCES[@]}"; do
  ssh proxmox "pct exec $CONTAINER -- bash -c 'cat > $BUILD_DIR/$f'" < "$SCRIPT_DIR/$f"
  echo "  ✓ $f"
done
for a in "${ASSETS[@]}"; do
  ssh proxmox "pct exec $CONTAINER -- bash -c 'cat > $BUILD_DIR/$a'" < "$SCRIPT_DIR/$a"
  echo "  ✓ $a"
done

# ── Optional: update pip packages ────────────────────────────────────────────
if [[ $UPDATE_DEPS -eq 1 ]]; then
  echo "[*] Updating pip packages..."
  ssh proxmox "pct exec $CONTAINER -- bash -c '
    export WINEDEBUG=-all WINEPREFIX=$WINEPREFIX
    Xvfb :99 -screen 0 1024x768x24 &>/dev/null &
    sleep 1
    DISPLAY=:99 wine C:\\\\Python311\\\\python.exe -m pip install -q --upgrade \
      paho-mqtt pystray Pillow requests pyinstaller
    kill %1 2>/dev/null; true
  '" 2>&1 | grep -v "^$" || true
fi

# ── Build ─────────────────────────────────────────────────────────────────────
echo "[3/4] Building ${EXE_FILE}..."
BUILD_LOG=$(ssh proxmox "pct exec $CONTAINER -- bash -c '
  export WINEDEBUG=-all WINEPREFIX=$WINEPREFIX
  pkill Xvfb 2>/dev/null; sleep 1
  Xvfb :99 -screen 0 1024x768x24 &>/dev/null &
  sleep 1
  cd $BUILD_DIR
  rm -rf build dist ${EXE_NAME}.spec
  DISPLAY=:99 wine $PYINSTALLER \
    --onefile --windowed --name ${EXE_NAME} \
    --icon assets/icon.ico \
    --add-data "assets;assets" \
    --hidden-import pystray._win32 \
    --hidden-import PIL._tkinter_finder \
    main.py 2>&1
  pkill Xvfb 2>/dev/null; true
'" 2>&1)

if echo "$BUILD_LOG" | grep -q "Build complete"; then
  echo "  Build complete!"
else
  echo "  Build FAILED. Last 20 lines:"
  echo "$BUILD_LOG" | tail -20
  exit 1
fi

# ── Fetch exe ─────────────────────────────────────────────────────────────────
echo "[4/4] Fetching ${EXE_FILE}..."

# Alte .exe Dateien entfernen
rm -f "$SCRIPT_DIR"/SOOHA*.exe

ssh proxmox "pct exec $CONTAINER -- bash -c 'cat $BUILD_DIR/dist/${EXE_FILE}'" \
  > "$SCRIPT_DIR/${EXE_FILE}"

SIZE=$(ls -lh "$SCRIPT_DIR/${EXE_FILE}" | awk '{print $5}')
echo ""
echo "  Done: ${EXE_FILE} (${SIZE})"
echo "  Path: $SCRIPT_DIR/${EXE_FILE}"
