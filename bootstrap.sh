#!/usr/bin/env bash
# Bootstrap WhatsApp automation dependencies on Amazon Linux 2023 (Corretto 17 image)
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run this script as root (e.g. sudo $0)" >&2
  exit 1
fi

echo "[1/5] Updating base system packages..."
dnf update -y

echo "[2/5] Installing core tools and Chrome dependencies..."
dnf install -y \
  python3 \
  python3-pip \
  git \
  unzip \
  fontconfig \
  libX11 \
  libXcomposite \
  libXcursor \
  libXdamage \
  libXext \
  libXi \
  libXrandr \
  libXrender \
  libXtst \
  mesa-libEGL \
  mesa-libgbm \
  alsa-lib \
  cups-libs \
  atk \
  at-spi2-atk \
  liberation-fonts \
  libdrm \
  which

if [[ ! -f /etc/yum.repos.d/google-chrome.repo ]]; then
  echo "[3/5] Adding Google Chrome repository..."
  cat <<'EOF' > /etc/yum.repos.d/google-chrome.repo
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/$basearch
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
EOF
fi

echo "[4/5] Installing Google Chrome Stable..."
dnf install -y google-chrome-stable

echo "[5/5] Upgrading pip and installing Python dependencies..."
python3 -m pip install --upgrade pip wheel
python3 -m pip install --upgrade selenium undetected-chromedriver

echo "Bootstrap complete. Reboot the instance or restart services if needed."

echo "Launching WhatsApp automation headless auth..."
python3 whatsapp_automation_test_ec2_auth.py
