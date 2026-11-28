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


def run_agent(root, model, draft=None):
    usage = getattr(model, "usage", ajan.Usage())
    return ajan.run(root, model, "test-model", "2026-11-28", usage, draft_loader=lambda _task_id: draft)


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
    result = run_agent(root, model)

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
    result = run_agent(root, model)
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
    result = run_agent(root, model)
    assert result.ok
    assert len(model.prompts) == 3
    assert "Test çıktısı (başarısız)" in model.prompts[2]
    assert "düzeltildi" in (root / ".ajan" / "pr_aciklama.md").read_text(encoding="utf-8")


def test_run_failure_saves_draft_and_writes_no_pr(tmp_path):
    root = make_repo(tmp_path)
    responses = [{"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""}]
    responses += [{"files": files(("src/pkg/add.py", BAD_CODE)), "notes": ""}] * (1 + ajan.MAX_FIXES)
    model = FakeModel(responses)
    result = run_agent(root, model)

    assert not result.ok
    assert "geçmedi" in result.message
    assert "Yarım kalan iş kaydedildi (1/3)" in result.message
    state = json.loads((root / ajan.DRAFT_STATE).read_text(encoding="utf-8"))
    assert state["task_id"] == "G-001"
    assert state["phase"] == "code"
    assert state["failed_runs"] == 1
    assert state["files"] == ["src/pkg/add.py", "tests/test_add.py"]
    assert not (root / ".ajan" / "pr_baslik.txt").exists()
    assert "## [ ] G-001:" in (root / "BACKLOG.md").read_text(encoding="utf-8")


def test_run_quota_exhausted_saves_draft_without_counting_failure(tmp_path):
    root = make_repo(tmp_path)

    def model(prompt):
        if "Bu adım: kod" in prompt:
            raise ajan.QuotaExhausted("Günlük istek kotası doldu.")
        return {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""}

    result = run_agent(root, model)
    assert not result.ok
    assert "09:00" in result.message
    assert "kaldığı yerden devam" in result.message
    state = json.loads((root / ajan.DRAFT_STATE).read_text(encoding="utf-8"))
    assert state["phase"] == "tests"
    assert state["failed_runs"] == 0
    assert (root / "tests" / "test_add.py").is_file()


def test_quota_on_first_request_saves_nothing(tmp_path):
    root = make_repo(tmp_path)

    def model(prompt):
        raise ajan.QuotaExhausted("Günlük istek kotası doldu.")

    result = run_agent(root, model)
    assert not result.ok
    assert not (root / ajan.DRAFT_STATE).exists()


def draft_state(phase, failed_runs, file_map):
    return {"state": {"task_id": "G-001", "phase": phase, "failed_runs": failed_runs,
                      "files": sorted(file_map), "info": {"summary": "Toplama eklendi."}, "warnings": []},
            "files": file_map}


def test_resume_from_code_phase_goes_straight_to_fix(tmp_path):
    root = make_repo(tmp_path)
    draft = draft_state("code", 1, {"tests/test_add.py": TEST_FILE, "src/pkg/add.py": BAD_CODE})
    model = FakeModel([{"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "İşaret düzeltildi."}])
    result = run_agent(root, model, draft)

    assert result.ok, result.message
    assert len(model.prompts) == 1
    assert "Bu adım: düzeltme" in model.prompts[0]
    description = (root / ".ajan" / "pr_aciklama.md").read_text(encoding="utf-8")
    assert description.startswith("Toplama eklendi.")
    assert "taslak/G-001" in description


def test_resume_from_tests_phase_skips_test_step(tmp_path):
    root = make_repo(tmp_path)
    draft = draft_state("tests", 0, {"tests/test_add.py": TEST_FILE})
    model = FakeModel([{"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "ok"}])
    result = run_agent(root, model, draft)

    assert result.ok, result.message
    assert len(model.prompts) == 1
    assert "Bu adım: kod" in model.prompts[0]
    assert "ModuleNotFoundError" in model.prompts[0] or "No module named" in model.prompts[0]


def test_stops_after_max_failed_runs_without_requests(tmp_path):
    root = make_repo(tmp_path)
    draft = draft_state("code", ajan.MAX_FAILED_RUNS, {"tests/test_add.py": TEST_FILE, "src/pkg/add.py": BAD_CODE})
    model = FakeModel([])
    result = run_agent(root, model, draft)

    assert not result.ok
    assert model.prompts == []
    assert "taslak/G-001" in result.message
    assert not (root / "src" / "pkg" / "add.py").exists()


def test_load_draft_reads_branch_from_origin(tmp_path):
    import subprocess

    def git(cwd, *args):
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "--bare", "-q", str(origin))
    work = tmp_path / "work"
    git(tmp_path, "clone", "-q", str(origin), str(work))
    git(work, "config", "user.email", "t@example.com")
    git(work, "config", "user.name", "t")
    (work / "README.md").write_text("x\n", encoding="utf-8")
    git(work, "add", "README.md")
    git(work, "commit", "-q", "-m", "ilk")
    git(work, "push", "-q", "origin", "HEAD:refs/heads/main")
    git(work, "checkout", "-q", "-b", "taslak/G-001")
    (work / "tests").mkdir()
    (work / "tests" / "test_add.py").write_text(TEST_FILE, encoding="utf-8")
    state = {"task_id": "G-001", "phase": "tests", "failed_runs": 0, "files": ["tests/test_add.py"]}
    (work / ajan.DRAFT_STATE).write_text(json.dumps(state), encoding="utf-8")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "taslak")
    git(work, "push", "-q", "origin", "taslak/G-001")

    clone = tmp_path / "clone"
    git(tmp_path, "clone", "-q", "--branch", "main", str(origin), str(clone))
    draft = ajan.load_draft(clone, "G-001")
    assert draft["state"]["phase"] == "tests"
    assert draft["files"] == {"tests/test_add.py": TEST_FILE}
    assert ajan.load_draft(clone, "G-002") is None


def test_run_rejects_task_without_test_file(tmp_path):
    root = make_repo(tmp_path)
    (root / "BACKLOG.md").write_text("## [ ] G-009: Testsiz\n\n**Dokunulacak dosyalar:** `src/a.py`\n", encoding="utf-8")
    result = run_agent(root, FakeModel([]))
    assert not result.ok
    assert "test dosyası yok" in result.message


def test_run_records_decision(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""},
        {"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "ok",
         "decision": "Toplama için yerleşik + kullanıldı\n- **Neden:** basit."},
    ])
    assert run_agent(root, model).ok
    decisions = (root / "KARARLAR.md").read_text(encoding="utf-8")
    assert "## 2026-11-28 · Toplama için yerleşik + kullanıldı" in decisions
    assert "- **Neden:** basit." in decisions


def test_fix_step_does_not_overwrite_code_summary(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""},
        {"files": files(("src/pkg/add.py", BAD_CODE)), "notes": "", "summary": "Toplama eklendi.",
         "progress_note": "Toplama eklendi"},
        {"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "İşaret düzeltildi.",
         "progress_note": "İşaret düzeltildi"},
    ])
    assert run_agent(root, model).ok
    description = (root / ".ajan" / "pr_aciklama.md").read_text(encoding="utf-8")
    assert description.startswith("Toplama eklendi.")
    assert "- Düzeltme 1: İşaret düzeltildi." in description
    assert "Toplama eklendi" in (root / "ILERLEME.md").read_text(encoding="utf-8")


def test_decision_without_reason_is_not_recorded(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""},
        {"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "ok",
         "decision": "Birlik sağlandı, testler yeşil dönecek."},
    ])
    result = run_agent(root, model)
    assert result.ok
    assert (root / "KARARLAR.md").read_text(encoding="utf-8") == "# Kararlar\n"
    assert "gerekçesiz" in " ".join(result.details)


def test_context_includes_rules_but_not_task_files_or_backlog(tmp_path):
    root = make_repo(tmp_path)
    (root / "src" / "pkg" / "add.py").write_text("ESKI_ICERIK\n", encoding="utf-8")
    context = ajan.build_context(root, exclude=["src/pkg/add.py"])
    assert "<<<DOSYA: AGENTS.md>>>" in context
    assert "<<<DOSYA: src/pkg/__init__.py>>>" in context
    assert "ESKI_ICERIK" not in context
    assert "<<<DOSYA: BACKLOG.md>>>" not in context


# --- Model istemcisi (sahte ağ) ------------------------------------------------


import io
import urllib.error


def ok_response(payload):
    body = {"candidates": [{"content": {"parts": [{"text": json.dumps(payload)}]}}],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5}}
    return io.BytesIO(json.dumps(body).encode("utf-8"))


def http_error(code, body=""):
    return urllib.error.HTTPError("https://example.test", code, "hata", {}, io.BytesIO(body.encode("utf-8")))


def fake_network(monkeypatch, outcomes):
    """Her istekte sıradaki sonucu döndürür; istenen modelleri kaydeder."""
    seen = []

    def urlopen(request, timeout):
        seen.append(request.full_url.split("/models/")[1].split(":")[0])
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(ajan.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(ajan.time, "sleep", lambda seconds: None)
    return seen


def test_client_switches_to_fallback_after_two_server_errors(monkeypatch):
    seen = fake_network(monkeypatch, [http_error(503), TimeoutError("zaman aşımı"), ok_response({"files": [], "notes": "ok"})])
    client = ajan.GeminiClient("ana", "anahtar", min_gap=0, fallback_model="yedek")
    assert client("istek") == {"files": [], "notes": "ok"}
    assert seen == ["ana", "ana", "yedek"]
    assert client.usage.models == ["yedek"]
    assert client.usage.model_label("ana") == "yedek"


def test_client_switches_to_fallback_when_daily_quota_is_exhausted(monkeypatch):
    daily = quota_body("GenerateRequestsPerDayPerProjectPerModel-FreeTier")
    seen = fake_network(monkeypatch, [http_error(429, daily), ok_response({"files": [], "notes": ""})])
    client = ajan.GeminiClient("ana", "anahtar", min_gap=0, fallback_model="yedek")
    client("istek")
    assert seen == ["ana", "yedek"]


def test_client_raises_quota_exhausted_when_fallback_also_exhausted(monkeypatch):
    daily = quota_body("GenerateRequestsPerDayPerProjectPerModel-FreeTier")
    fake_network(monkeypatch, [http_error(429, daily), http_error(429, daily)])
    client = ajan.GeminiClient("ana", "anahtar", min_gap=0, fallback_model="yedek")
    try:
        client("istek")
    except ajan.QuotaExhausted:
        pass
    else:
        raise AssertionError("QuotaExhausted bekleniyordu")


def test_client_raises_service_unavailable_after_repeated_server_errors(monkeypatch):
    fake_network(monkeypatch, [http_error(503)] * 6)
    client = ajan.GeminiClient("ana", "anahtar", min_gap=0)
    try:
        client("istek")
    except ajan.ServiceUnavailable as err:
        assert "503" in str(err)
    else:
        raise AssertionError("ServiceUnavailable bekleniyordu")


def test_client_does_not_retry_client_errors(monkeypatch):
    seen = fake_network(monkeypatch, [http_error(400, "kötü istek")])
    client = ajan.GeminiClient("ana", "anahtar", min_gap=0, fallback_model="yedek")
    try:
        client("istek")
    except ajan.ModelError as err:
        assert "HTTP 400" in str(err)
    assert seen == ["ana"]


def test_run_service_unavailable_does_not_count_as_failed_run(tmp_path):
    root = make_repo(tmp_path)

    def model(prompt):
        if "Bu adım: kod" in prompt:
            raise ajan.ServiceUnavailable("Google'ın sunucuları cevap vermedi. Sunucu hatası 503.")
        return {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""}

    result = run_agent(root, model)
    assert not result.ok
    assert "kaldığı yerden devam" in result.message
    state = json.loads((root / ajan.DRAFT_STATE).read_text(encoding="utf-8"))
    assert state["failed_runs"] == 0
    assert state["phase"] == "tests"


def test_progress_line_names_the_model_that_answered(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""},
        {"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "ok"},
    ])
    model.usage.models = ["yedek-model"]
    assert run_agent(root, model).ok
    assert "(ajan: yedek-model, 2 istek)" in (root / "ILERLEME.md").read_text(encoding="utf-8")


def test_progress_note_repeating_the_line_is_dropped(tmp_path):
    root = make_repo(tmp_path)
    model = FakeModel([
        {"files": files(("tests/test_add.py", TEST_FILE)), "notes": ""},
        {"files": files(("src/pkg/add.py", GOOD_CODE)), "notes": "", "summary": "ok",
         "progress_note": "G-001: Toplama fonksiyonu · Öneri açıldı"},
    ])
    assert run_agent(root, model).ok
    last = (root / "ILERLEME.md").read_text(encoding="utf-8").splitlines()[-1]
    assert last.count("Toplama fonksiyonu") == 1
