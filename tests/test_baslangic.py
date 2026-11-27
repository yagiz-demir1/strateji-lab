"""İskeletin çalıştığını gösteren ilk test."""

import stratlab


def test_paket_yukleniyor():
    assert stratlab.__version__ == "0.1.0"
