#!/bin/bash
# One-time setup for a Build to Survive run. Usage: bash SETUP.sh (from the engine folder)
set -e
pip install --break-system-packages -q kokoro-onnx soundfile pycairo numpy scipy pillow 2>&1 | grep -v WARNING | tail -1 || true
mkdir -p ~/mwmodels ~/.fonts
[ -f ~/mwmodels/kokoro-v1.0.onnx ] || curl -sSL -o ~/mwmodels/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f ~/mwmodels/voices-v1.0.bin ] || curl -sSL -o ~/mwmodels/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ~/.fonts
for f in ofl/archivoblack/ArchivoBlack-Regular.ttf ofl/poppins/Poppins-Bold.ttf ofl/poppins/Poppins-SemiBold.ttf; do
  n=$(basename "$f"); [ -f "$n" ] || curl -sSLO "https://raw.githubusercontent.com/google/fonts/main/$f"; done
fc-cache -f >/dev/null
echo SETUP_OK
