#!/usr/bin/env bash
# Ortamı kurar: Python paketlerini yükler.
# Kullanım: bash setup.sh
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Kurulum tamam. Testler için: python -m pytest"
