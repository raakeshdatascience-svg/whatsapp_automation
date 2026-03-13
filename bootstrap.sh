#!/usr/bin/env bash
# Bootstrap WhatsApp automation dependencies on Ubuntu (e.g., 22.04+)
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run this script as root (e.g. sudo $0)" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "[1/6] Updating apt metadata..."
apt-get update -y

echo "[2/6] Upgrading existing packages (safe upgrade)..."
apt-get upgrade -y

ASOUND_PKG=libasound2
if ! apt-cache show "${ASOUND_PKG}" >/dev/null 2>&1; then
  ASOUND_PKG=libasound2t64
fi

echo "[3/6] Installing core tools and Chrome dependencies..."
apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  git \
  unzip \
  fontconfig \
  libx11-6 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxtst6 \
  libxrandr2 \
  libxrender1 \
  libxi6 \
  libnss3 \
  libatk-bridge2.0-0 \
  libgtk-3-0 \
  libdrm2 \
  libgbm1 \
  "${ASOUND_PKG}" \
  libcups2 \
  libglib2.0-0 \
  libatk1.0-0 \
  libpangocairo-1.0-0 \
  libxkbcommon0 \
  fonts-liberation \
  ca-certificates \
  curl \
  gnupg \
  software-properties-common

if [[ ! -f /etc/apt/sources.list.d/google-chrome.list ]]; then
  echo "[4/6] Adding Google Chrome repository..."
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-linux.gpg
  chmod go+r /etc/apt/keyrings/google-linux.gpg
  cat <<'EOF' > /etc/apt/sources.list.d/google-chrome.list
deb [arch=amd64 signed-by=/etc/apt/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main
EOF
  apt-get update -y
fi

echo "[5/6] Installing Google Chrome Stable..."
apt-get install -y google-chrome-stable

VENV_DIR="${VENV_DIR:-.venv}"
if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[6/6] Creating Python virtual environment at ${VENV_DIR}..."
  python3 -m venv "${VENV_DIR}"
else
  echo "[6/6] Reusing existing Python virtual environment at ${VENV_DIR}..."
fi

PIP_BIN="${VENV_DIR}/bin/pip"
PY_BIN="${VENV_DIR}/bin/python"
echo "Installing Python dependencies in ${VENV_DIR}..."
"${PIP_BIN}" install --upgrade pip wheel
"${PIP_BIN}" install --upgrade selenium undetected-chromedriver

echo "Bootstrap complete. Reboot the instance or restart services if needed."

echo "Launching WhatsApp automation headless auth..."
"${PY_BIN}" whatsapp_automation_test_ec2_auth.py
