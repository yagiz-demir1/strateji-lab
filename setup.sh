#!/usr/bin/env bash
# Ortamı kurar: Python paketlerini yükler.
# Kullanım: bash setup.sh
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# Projenin kendisi (src/stratlab) düzenlenebilir modda kurulur; böylece
# 'python -m stratlab.run' ve 'streamlit run src/stratlab/ui/app.py' her klasörden çalışır.
python -m pip install -e .

echo "Kurulum tamam. Testler için: python -m pytest"
