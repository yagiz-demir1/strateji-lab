"""ajan.py testleri. Çalıştırma: python -m pytest .github/ajan -q"""

import json
import textwrap

import ajan

BACKLOG = textwrap.dedent("""\
    # Görev listesi

    ## Faz 1 – Çekirdek

    ## [x] G-000: Yapılmış görev

    **Dokunulacak dosyalar:** `src/eski.py`

    ## [ ] G-001: Toplama fonksiyonu

    **Hedef:** İki sayıyı toplamak.

    **Bitme şartı (test):**
    - `add(2, 3)` → `5`

    **Dokunulacak dosyalar:** `src/pkg/add.py`, `tests/test_add.py`, `../disari.py`, `HEDEF.md`, `.github/workflows/x.yml`

    **Kapsam dışı:** Diğer işlemler.

    ## [ ] G-002: Sonraki görev

    **Dokunulacak dosyalar:** `src/pkg/sub.py`, `tests/test_sub.py`
    """)

TEST_FILE = "from pkg.add import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n"
GOOD_CODE = '"""Toplama."""\n\n\ndef add(a, b):\n    return a + b\n'
BAD_CODE = '"""Toplama."""\n\n\ndef add(a, b):\n    return a - b\n'


def make_repo(tmp_path):
    (tmp_path / "BACKLOG.md").write_text(BACKLOG, encoding="utf-8")
    (tmp_path / "ILERLEME.md").write_text("# İlerleme\n\n- 2026-11-27 · Kurulum · tamam\n", encoding="utf-8")
    (tmp_path / "KARARLAR.md").write_text("# Kararlar\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Ajan talimatları\n", encoding="utf-8")
    (tmp_path / "HEDEF.md").write_text("# Hedef\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\npythonpath = ["src"]\ntestpaths = ["tests"]\n', encoding="utf-8")
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    return tmp_path


class FakeModel:
    """Sırayla hazır yanıtlar döndürür ve gelen istekleri saklar."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []
        self.usage = ajan.Usage()

    def __call__(self, prompt):
        self.prompts.append(prompt)
        self.usage.requests += 1
        return self.responses.pop(0)


def files(*pairs):
    return [{"path": path, "content": content} for path, content in pairs]


# --- Görev ve yollar ---------------------------------------------------------


def test_find_task_returns_first_unchecked_task_section():
    task = ajan.find_task(BACKLOG)
    assert task.task_id == "G-001"
    assert task.title == "Toplama fonksiyonu"
    assert task.body.startswith("## [ ] G-001")
    assert "G-002" not in task.body
    assert "Kapsam dışı" in task.body


def test_find_task_returns_none_when_all_done():
    assert ajan.find_task("## [x] G-001: Bitti\n") is None


def test_allowed_files_drops_unsafe_and_protected_paths():
    task = ajan.find_task(BACKLOG)
    assert ajan.allowed_files(task.body) == ["src/pkg/add.py", "tests/test_add.py"]


def test_normalize_rejects_paths_outside_repo():
    assert ajan.normalize("./src/a.py") == "src/a.py"
    assert ajan.normalize("../a.py") is None
    assert ajan.normalize("/etc/passwd") is None
    assert ajan.normalize("src\\a.py") is None
    assert ajan.normalize("") is None


def test_mark_done_changes_only_given_task():
    result = ajan.mark_done(BACKLOG, "G-001")
    assert "## [x] G-001:" in result
    assert "## [ ] G-002:" in result


def test_is_test_file():
    assert ajan.is_test_file("tests/test_add.py")
    assert not ajan.is_test_file("tests/helpers.py")
    assert not ajan.is_test_file("tests/fixtures/test.csv")


# --- Model yanıtları ---------------------------------------------------------


def quota_body(quota_id, delay="55s"):
    return json.dumps({"error": {"code": 429, "details": [
        {"@type": "type.googleapis.com/google.rpc.QuotaFailure", "violations": [{"quotaId": quota_id}]},
        {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": delay},
    ]}})


def test_classify_quota_error_daily():
    daily, _ = ajan.classify_quota_error(quota_body("GenerateRequestsPerDayPerProjectPerModel-FreeTier"))
    assert daily


def test_classify_quota_error_per_minute_with_delay():
    daily, delay = ajan.classify_quota_error(quota_body("GenerateRequestsPerMinutePerProjectPerModel-FreeTier", "1.5s"))
    assert not daily
    assert delay == 1.5


def test_classify_quota_error_unreadable_body():
    assert ajan.classify_quota_error("<html>") == (False, 60.0)


def test_extract_text_skips_thoughts():
    data = {"candidates": [{"content": {"parts": [{"text": "düşünce", "thought": True}, {"text": "{\"a\": 1}"}]}}]}
    assert ajan.extract_text(data) == '{"a": 1}'


# --- Dosya yazma -------------------------------------------------------------


def test_file_writer_rejects_unlisted_paths_and_restores(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "var.py").write_text("eski\n", encoding="utf-8")
    writer = ajan.FileWriter(tmp_path, ["src/var.py", "src/yeni.py"])
    changed = writer.apply([
        {"path": "src/var.py", "content": "yeni"},
        {"path": "src/yeni.py", "content": "x"},
        {"path": "HEDEF.md", "content": "silindi"},
        {"path": "../disari.py", "content": "x"},
    ])
    assert changed == ["src/var.py", "src/yeni.py"]
    assert writer.rejected == ["HEDEF.md", "../disari.py"]
    assert not (tmp_path / "HEDEF.md").exists()
    writer.restore()
    assert (tmp_path / "src" / "var.py").read_text(encoding="utf-8") == "eski\n"
    assert not (tmp_path / "src" / "yeni.py").exists()


# --- Uçtan uca (sahte model, gerçek pytest) ------------------------------------


def test_run_success_updates_backlog_progress_and_writes_pr_files(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""},
        {"files": files(("src/pkg/add.py", GOOD_CODE), ("HEDEF.md", "bozuldu")), "notes": "",
         "summary": "Toplama eklendi.", "progress_note": "Toplama eklendi", "decision": ""},
    ])
    result = ajan.run(root, model, "test-model", "2026-11-28", model.usage)

    assert result.ok, result.message
    assert len(model.prompts) == 2
    assert "## [x] G-001:" in (root / "BACKLOG.md").read_text(encoding="utf-8")
    assert "## [ ] G-002:" in (root / "BACKLOG.md").read_text(encoding="utf-8")
    assert "2026-11-28 · G-001: Toplama fonksiyonu · Öneri açıldı" in (root / "ILERLEME.md").read_text(encoding="utf-8")
    assert (root / ".ajan" / "pr_baslik.txt").read_text(encoding="utf-8").strip() == "G-001: Toplama fonksiyonu"
    description = (root / ".ajan" / "pr_aciklama.md").read_text(encoding="utf-8")
    assert "Toplama eklendi." in description
    assert "`HEDEF.md`" in description  # reddedilen yol açıklamada uyarı olarak görünür
    assert (root / "HEDEF.md").read_text(encoding="utf-8") == "# Hedef\n"
    assert (root / "tests" / "test_add.py").is_file()


def test_run_test_phase_cannot_write_code(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE), ("src/pkg/add.py", GOOD_CODE)), "notes": ""},
        {"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "ok"},
    ])
    result = ajan.run(root, model, "test-model", "2026-11-28", model.usage)
    assert result.ok
    assert "Testler kod yazılmadan önce de geçti" not in " ".join(result.details)
    assert "src/pkg/add.py" in " ".join(result.details)  # ilk adımda reddedildi


def test_run_fixes_code_after_failure(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""},
        {"files": files(("src/pkg/add.py", BAD_CODE)), "notes": "", "summary": "ilk"},
        {"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "düzeltildi"},
    ])
    result = ajan.run(root, model, "test-model", "2026-11-28", model.usage)
    assert result.ok
    assert len(model.prompts) == 3
    assert "Test çıktısı (başarısız)" in model.prompts[2]
    assert "düzeltildi" in (root / ".ajan" / "pr_aciklama.md").read_text(encoding="utf-8")


def test_run_failure_restores_files_and_writes_no_pr(tmp_path):
    root = make_repo(tmp_path)
    responses = [{"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""}]
    responses += [{"files": files(("src/pkg/add.py", BAD_CODE)), "notes": ""}] * (1 + ajan.MAX_FIXES)
    model = FakeModel(responses)
    result = ajan.run(root, model, "test-model", "2026-11-28", model.usage)

    assert not result.ok
    assert "geçmedi" in result.message
    assert not (root / "tests" / "test_add.py").exists()
    assert not (root / "src" / "pkg" / "add.py").exists()
    assert not (root / ".ajan" / "pr_baslik.txt").exists()
    assert "## [ ] G-001:" in (root / "BACKLOG.md").read_text(encoding="utf-8")


def test_run_quota_exhausted_restores_files(tmp_path):
    root = make_repo(tmp_path)

    def model(prompt):
        if "Bu adım: kod" in prompt:
            raise ajan.QuotaExhausted("Günlük istek kotası doldu.")
        return {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""}

    result = ajan.run(root, model, "test-model", "2026-11-28", ajan.Usage())
    assert not result.ok
    assert "09:00" in result.message
    assert not (root / "tests" / "test_add.py").exists()


def test_run_rejects_task_without_test_file(tmp_path):
    root = make_repo(tmp_path)
    (root / "BACKLOG.md").write_text("## [ ] G-009: Testsiz\n\n**Dokunulacak dosyalar:** `src/a.py`\n", encoding="utf-8")
    result = ajan.run(root, FakeModel([]), "test-model", "2026-11-28", ajan.Usage())
    assert not result.ok
    assert "test dosyası yok" in result.message


def test_run_records_decision(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""},
        {"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "ok",
         "decision": "Toplama için yerleşik + kullanıldı\n- **Neden:** basit."},
    ])
    assert ajan.run(root, model, "test-model", "2026-11-28", model.usage).ok
    decisions = (root / "KARARLAR.md").read_text(encoding="utf-8")
    assert "## 2026-11-28 · Toplama için yerleşik + kullanıldı" in decisions
    assert "- **Neden:** basit." in decisions


def test_context_includes_rules_but_not_task_files_or_backlog(tmp_path):
    root = make_repo(tmp_path)
    (root / "src" / "pkg" / "add.py").write_text("ESKI_ICERIK\n", encoding="utf-8")
    context = ajan.build_context(root, exclude=["src/pkg/add.py"])
    assert "<<<DOSYA: AGENTS.md>>>" in context
    assert "<<<DOSYA: src/pkg/__init__.py>>>" in context
    assert "ESKI_ICERIK" not in context
    assert "<<<DOSYA: BACKLOG.md>>>" not in context
