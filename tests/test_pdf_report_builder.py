from pathlib import Path
import zipfile

import pytest

from fit_common.core.pdf_report_builder import PdfReportBuilder, ReportType


def _translations():
    return {
        "DOCUMENT_TITLE": "Doc",
        "DOCUMENT_SUBTITLE": "Sub",
        "APPLICATION_SHORT_NAME": "FIT",
        "SECTION_DESCRIPTION_FIT_APPLICATION": "See {}",
        "RELEASES_LINK": "https://example.test/releases",
        "SECTION_TITLE_DIGITAL_FORENSICS": "Digital Forensics",
        "SECTION_DESCRIPTION_DIGITAL_FORENSICS": "Description",
        "SECTION_TITLE_CHAIN_OF_CUSTODY": "Chain",
        "SECTION_TITLE_HASHES": "Hashes",
        "SECTION_DESCRIPTION_CHAIN_OF_CUSTODY": "Chain desc",
        "SECTION_DESCRIPTION_HASHES": "Hashes desc",
        "SECTION_TITLE_WACZ": "WACZ",
        "SECTION_DESCRIPTION_WACZ": "WACZ desc",
        "TABLE_ROW_LABEL_CASE": "Case",
        "TABLE_ROW_LABEL_LAWYER": "Lawyer",
        "TABLE_ROW_LABEL_OPERATOR": "Operator",
        "TABLE_ROW_LABEL_PROCEEDING": "Proceeding",
        "TABLE_ROW_LABEL_COURT": "Court",
        "TABLE_ROW_LABEL_PROCEEDING_NUMBER": "Proceeding number",
        "ACQUISITION_TYPE": "Acquisition type",
        "ACQUISITION_DATE": "Acquisition date",
        "SECTION_TITLE_GENERAL_INFORMATION": "General",
        "TABLE_COLUMN_CASE_INFO": "Field",
        "TABLE_COLUMN_CASE_DATA": "Value",
        "SECTION_TITLE_VERIFICATION": "Verification",
        "VERIFI_OK": "OK",
        "VERIFI_KO": "KO",
        "INDEX": "Index",
        "NOTE": "Note",
        "PAGE": "Page",
        "OF": "of",
        "EMPTY_FILE": "{} is empty",
        "SIZE": "Size: ",
        "SCREENSHOT_LINK_LABEL": "Screenshot",
        "VIDEO_LINK_LABEL": "Video",
    }


def _write_png(path: Path, width: int, height: int):
    signature = b"\x89PNG\r\n\x1a\n"
    length = (13).to_bytes(4, "big")
    chunk_type = b"IHDR"
    data = width.to_bytes(4, "big") + height.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00"
    crc = b"\x00\x00\x00\x00"
    path.write_bytes(signature + length + chunk_type + data + crc)


class _FakeTemplate:
    def render(self, **kwargs):
        return "html"


class _FakeResource:
    def __init__(self, package_name: str, name: str = ""):
        self.package_name = package_name
        self.name = name

    def __truediv__(self, other: str):
        return _FakeResource(self.package_name, other)

    def read_bytes(self):
        if self.package_name == "fit_assets.images" and self.name == "logo-640x640.png":
            return b"logo-bytes"
        raise FileNotFoundError(self.name)

    def read_text(self, encoding="utf-8"):
        if self.package_name == "fit_assets.templates" and self.name in {"front.html", "content.html"}:
            return "<html>{{ document_title }}</html>"
        raise FileNotFoundError(self.name)


class _FakePdfReader:
    def __init__(self, file_obj):
        self.pages = [object()]


class _FakePdfWriter:
    def __init__(self):
        self._pages = []

    def add_page(self, page):
        self._pages.append(page)

    def write(self, file_obj):
        file_obj.write(b"%PDF-1.4\n")


@pytest.fixture
def translations():
    return _translations()


def test_safe_text_none_and_trim():
    assert PdfReportBuilder._PdfReportBuilder__safe_text(None) == ""
    assert PdfReportBuilder._PdfReportBuilder__safe_text("  abc  ") == "abc"


def test_read_file_returns_none_for_missing_and_empty_and_blank(tmp_path, translations):
    builder = PdfReportBuilder(ReportType.VERIFY, translations=translations, path=str(tmp_path), filename="out.pdf")
    assert builder._PdfReportBuilder__read_file("missing.txt") is None

    (tmp_path / "empty.txt").write_text("", encoding="utf-8")
    assert builder._PdfReportBuilder__read_file("empty.txt") is None

    (tmp_path / "blank.txt").write_text("   \n", encoding="utf-8")
    assert builder._PdfReportBuilder__read_file("blank.txt") is None

    (tmp_path / "value.txt").write_text("abc", encoding="utf-8")
    assert builder._PdfReportBuilder__read_file("value.txt") == "abc"


def test_acquisition_files_marks_empty_and_detects_eml(tmp_path, translations):
    (tmp_path / "acquisition.log").write_text("", encoding="utf-8")
    (tmp_path / "timestamp.tsr").write_text("tsr", encoding="utf-8")
    (tmp_path / "mail.eml").write_text("eml", encoding="utf-8")

    builder = PdfReportBuilder(
        ReportType.ACQUISITION,
        translations=translations,
        path=str(tmp_path),
        filename="out.pdf",
        screen_recorder_filename="video.mp4",
        packet_capture_filename="capture.pcap",
    )
    files = builder._acquisition_files_names()

    assert "acquisition.log" in files
    assert files["acquisition.log"] == "acquisition.log is empty"
    assert files["mail.eml"] == "mail.eml"


def test_insert_screenshot_builds_link_and_scaled_size(tmp_path, translations):
    screenshot = tmp_path / "acquisition_page.png"
    _write_png(screenshot, width=1200, height=600)

    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")
    html = builder._PdfReportBuilder__insert_screenshot()

    assert f"file://{screenshot}" in html
    assert 'width="430"' in html
    assert 'height="215"' in html


def test_read_png_dimensions_invalid_header(tmp_path):
    path = tmp_path / "invalid.png"
    path.write_bytes(b"not-png")
    assert PdfReportBuilder._PdfReportBuilder__read_png_dimensions(str(path)) == (None, None)


def test_read_png_dimensions_valid_png(tmp_path):
    path = tmp_path / "valid.png"
    _write_png(path, width=640, height=480)
    assert PdfReportBuilder._PdfReportBuilder__read_png_dimensions(str(path)) == (640, 480)


def test_insert_screenshot_returns_empty_when_file_missing(tmp_path, translations):
    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")
    assert builder._PdfReportBuilder__insert_screenshot() == ""


def test_insert_screenshot_uses_fallback_size_on_invalid_png(tmp_path, translations):
    screenshot = tmp_path / "acquisition_page.png"
    screenshot.write_text("not a png", encoding="utf-8")

    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")
    html = builder._PdfReportBuilder__insert_screenshot()

    assert 'width="430"' in html
    assert 'height="520"' in html


def test_force_wrap_splits_text_with_given_chunk_size(tmp_path, translations):
    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")
    wrapped = builder._PdfReportBuilder__force_wrap("abcdefghij", every=4)
    assert wrapped == "abcd\nefgh\nij"


def test_pec_eml_filename_returns_none_for_invalid_path(translations):
    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path="/does/not/exist", filename="out.pdf")
    assert builder._PdfReportBuilder__pec_eml_filename() is None


def test_pec_eml_filename_detects_case_insensitive_extension(tmp_path, translations):
    (tmp_path / "message.EML").write_text("x", encoding="utf-8")
    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")
    assert builder._PdfReportBuilder__pec_eml_filename() == "message.EML"


def test_is_empty_file_true_for_missing_or_zero_and_false_for_non_empty(tmp_path, translations):
    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")

    assert builder._PdfReportBuilder__is_empty_file("missing.txt")

    (tmp_path / "empty.txt").write_text("", encoding="utf-8")
    assert builder._PdfReportBuilder__is_empty_file("empty.txt")

    (tmp_path / "full.txt").write_text("abc", encoding="utf-8")
    assert not builder._PdfReportBuilder__is_empty_file("full.txt")


def test_hash_reader_renders_lines_when_hash_file_present(tmp_path, translations):
    (tmp_path / "acquisition.hash").write_text("sha256 a\nsha1 b\n", encoding="latin-1")
    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")
    html = builder._PdfReportBuilder__hash_reader()
    assert "<p>sha256 a\n</p>" in html
    assert "<p>sha1 b\n</p>" in html


def test_hash_reader_returns_empty_string_when_hash_file_missing(tmp_path, translations):
    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")
    assert builder._PdfReportBuilder__hash_reader() == ""


def test_zip_files_enum_lists_zip_entries_and_sizes(tmp_path, translations):
    archive = tmp_path / "sample.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("nested/file.name.png", "abc")
        zf.writestr("empty.txt", "")

    builder = PdfReportBuilder(ReportType.ACQUISITION, translations=translations, path=str(tmp_path), filename="out.pdf")
    html = builder._zip_files_enum()

    assert "nested/file.name" in html
    assert "Size: 3 bytes" in html
    assert "empty.txt" not in html


def test_acquisition_files_supports_prefixed_matching_filename(tmp_path, translations):
    (tmp_path / "acquisition.log.2026-02-20").write_text("x", encoding="utf-8")
    builder = PdfReportBuilder(
        ReportType.ACQUISITION,
        translations=translations,
        path=str(tmp_path),
        filename="out.pdf",
        screen_recorder_filename="video.mp4",
        packet_capture_filename="capture.pcap",
    )
    files = builder._acquisition_files_names()
    assert "acquisition.log.2026-02-20" in files
    assert files["acquisition.log.2026-02-20"] == "acquisition.log.2026-02-20"


def test_generate_pdf_verify_writes_output_and_cleans_verify_info(tmp_path, translations, monkeypatch):
    verify_info = tmp_path / "verify_info.txt"
    verify_info.write_text("verify content", encoding="utf-8")
    output_name = "verification_report.pdf"

    builder = PdfReportBuilder(
        ReportType.VERIFY,
        translations=translations,
        path=str(tmp_path),
        filename=output_name,
        case_info={"name": "Case X"},
    )
    builder.ntp = "2026-02-20"
    builder.verify_result = True
    builder.verify_info_file_path = str(verify_info)

    monkeypatch.setattr("fit_common.core.pdf_report_builder.files", lambda package: _FakeResource(package))
    monkeypatch.setattr("fit_common.core.pdf_report_builder.get_version", lambda: "1.2.3")
    monkeypatch.setattr(
        "fit_common.core.pdf_report_builder.pisa.CreatePDF",
        lambda html, dest, options: dest.write(b"pdf"),
    )
    monkeypatch.setattr("fit_common.core.pdf_report_builder.PdfReader", _FakePdfReader)
    monkeypatch.setattr("fit_common.core.pdf_report_builder.PdfWriter", _FakePdfWriter)
    monkeypatch.setattr(
        PdfReportBuilder,
        "_PdfReportBuilder__load_template",
        lambda self, template: _FakeTemplate(),
    )

    builder.generate_pdf()

    assert (tmp_path / output_name).exists()
    assert not verify_info.exists()


def test_insert_video_hyperlink_returns_none_when_missing(tmp_path, translations):
    builder = PdfReportBuilder(
        ReportType.ACQUISITION,
        translations=translations,
        path=str(tmp_path),
        filename="out.pdf",
        screen_recorder_filename="video.mp4",
    )
    assert builder._PdfReportBuilder__insert_video_hyperlink() is None


def test_insert_video_hyperlink_returns_anchor_when_file_exists(tmp_path, translations):
    video = tmp_path / "video.mp4"
    video.write_text("video", encoding="utf-8")

    builder = PdfReportBuilder(
        ReportType.ACQUISITION,
        translations=translations,
        path=str(tmp_path),
        filename="out.pdf",
        screen_recorder_filename="video.mp4",
    )
    html = builder._PdfReportBuilder__insert_video_hyperlink()
    assert f"file://{video}" in html
    assert "Video" in html
