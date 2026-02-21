from pathlib import Path

import pytest

from fit_common.core.acquisition_type import AcquisitionType
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
        "TABLE_ROW_DESCRIPTION_REPORT": "report",
        "TABLE_ROW_DESCRIPTION_SCREEN_CAPTURE": "screen",
        "TABLE_ROW_DESCRIPTION_HASH": "hash",
        "TABLE_ROW_DESCRIPTION_LOG": "log",
        "TABLE_ROW_DESCRIPTION_PCAP": "pcap",
        "TABLE_ROW_DESCRIPTION_CASE_INFORMATION": "caseinfo",
        "TABLE_ROW_DESCRIPTION_SYSTEM_INFORMATION": "system",
        "TABLE_ROW_DESCRIPTION_TIMESTAMP_TSR": "tsr",
        "TABLE_ROW_DESCRIPTION_TSA_CERTIFICATE": "tsa",
        "TABLE_ROW_DESCRIPTION_WHOIS": "whois",
        "TABLE_ROW_DESCRIPTION_HEADERS": "headers",
        "TABLE_ROW_DESCRIPTION_NSLOOKUP": "nslookup",
        "TABLE_ROW_DESCRIPTION_CER": "cer",
        "TABLE_ROW_DESCRIPTION_SSLKEYLOG": "sslkey",
        "TABLE_ROW_DESCRIPTION_TRACEROUTE": "traceroute",
        "SECTION_TITLE_SYSTEM_ARTIFACTS": "Artifacts",
        "SECTION_DESCRIPTION_SYSTEM_ARTIFACTS": "Artifacts desc",
        "TABLE_COLUMN_FILE_NAME": "File",
        "TABLE_COLUMN_FILE_DESCRIPTION": "Description",
        "TABLE_ROW_DESCRIPTION_PAGE_SCREENSHOT": "page",
        "TABLE_ROW_DESCRIPTION_WACZ": "wacz",
        "TABLE_ROW_DESCRIPTION_MAIL_ACQUISITION": "mail",
        "TABLE_ROW_DESCRIPTION_ACQUISITION_ARCHIVE": "zip",
        "TABLE_ROW_DESCRIPTION_SCREENSHOTS_ARCHIVE": "sszip",
        "TABLE_ROW_DESCRIPTION_DOWNLOADS_ARCHIVE": "dlzip",
        "SECTION_TITLE_ACQUIRED_CONTENT": "Acquired",
        "SECTION_DESCRIPTION_ACQUIRED_CONTENT": "Acquired desc",
        "SECTION_TITLE_INTEGRITY_VERIFICATION": "Integrity",
        "SECTION_DESCRIPTION_INTEGRITY_VERIFICATION": "Integrity desc",
        "SECTION_TITLE_DATA_OWNERSHIP_VERIFICATION": "Ownership",
        "SECTION_DESCRIPTION_DATA_OWNERSHIP_VERIFICATION": "Ownership desc",
        "SECTION_TITLE_SCREENSHOTS": "Screenshots",
        "SECTION_DESCRIPTION_SCREENSHOTS": "Screenshot desc",
        "SECTION_TITLE_VIDEO_ACQUISITION": "Video",
        "SECTION_DESCRIPTION_VIDEO_ACQUISITION": "Video desc",
    }


class _FakeResource:
    def __init__(self, package_name: str, name: str = ""):
        self.package_name = package_name
        self.name = name

    def __truediv__(self, other: str):
        return _FakeResource(self.package_name, other)

    def read_bytes(self):
        return b"logo-bytes"

    def read_text(self, encoding="utf-8"):
        return "<html>{{ document_title }}</html>"


class _FakeFrontTemplate:
    def render(self, **kwargs):
        return "front-html"


class _CaptureTemplate:
    captured = []

    def __init__(self, _text):
        pass

    def render(self, **kwargs):
        _CaptureTemplate.captured.append(kwargs)
        return "content-html"


class _FakePdfReader:
    def __init__(self, _file_obj):
        self.pages = [object()]


class _FakePdfWriter:
    def __init__(self):
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)

    def write(self, out):
        out.write(b"%PDF")


@pytest.mark.contract
def test_pdf_report_builder_verify_contract_contains_verification_section(tmp_path, monkeypatch):
    _CaptureTemplate.captured.clear()
    info = tmp_path / "verify.txt"
    info.write_text("verify info", encoding="utf-8")

    builder = PdfReportBuilder(
        ReportType.VERIFY,
        translations=_translations(),
        path=str(tmp_path),
        filename="verify.pdf",
        case_info={"name": "case"},
    )
    builder.ntp = "2026-02-21"
    builder.verify_result = True
    builder.verify_info_file_path = str(info)

    monkeypatch.setattr("fit_common.core.pdf_report_builder.files", lambda package: _FakeResource(package))
    monkeypatch.setattr("fit_common.core.pdf_report_builder.get_version", lambda: "1.0.0")
    monkeypatch.setattr("fit_common.core.pdf_report_builder.Template", _CaptureTemplate)
    monkeypatch.setattr("fit_common.core.pdf_report_builder.PdfReader", _FakePdfReader)
    monkeypatch.setattr("fit_common.core.pdf_report_builder.PdfWriter", _FakePdfWriter)
    monkeypatch.setattr(
        "fit_common.core.pdf_report_builder.pisa.CreatePDF",
        lambda html, dest, options: dest.write(b"pdf"),
    )
    monkeypatch.setattr(
        PdfReportBuilder,
        "_PdfReportBuilder__load_template",
        lambda self, template_name: _FakeFrontTemplate(),
    )

    builder.generate_pdf()

    assert (tmp_path / "verify.pdf").exists()
    payload = _CaptureTemplate.captured[-1]
    types = [s["type"] for s in payload["sections"]]
    assert "verification_report" in types


@pytest.mark.contract
def test_pdf_report_builder_acquisition_contract_includes_core_sections(tmp_path, monkeypatch):
    _CaptureTemplate.captured.clear()
    (tmp_path / "acquisition.log").write_text("ok", encoding="utf-8")

    builder = PdfReportBuilder(
        ReportType.ACQUISITION,
        translations=_translations(),
        path=str(tmp_path),
        filename="acq.pdf",
        case_info={"name": "case"},
        screen_recorder_filename="video.mp4",
        packet_capture_filename="capture.pcap",
    )
    builder.acquisition_type = AcquisitionType.WEB
    builder.ntp = "2026-02-21"

    monkeypatch.setattr("fit_common.core.pdf_report_builder.files", lambda package: _FakeResource(package))
    monkeypatch.setattr("fit_common.core.pdf_report_builder.get_version", lambda: "1.0.0")
    monkeypatch.setattr("fit_common.core.pdf_report_builder.Template", _CaptureTemplate)
    monkeypatch.setattr("fit_common.core.pdf_report_builder.PdfReader", _FakePdfReader)
    monkeypatch.setattr("fit_common.core.pdf_report_builder.PdfWriter", _FakePdfWriter)
    monkeypatch.setattr(
        "fit_common.core.pdf_report_builder.pisa.CreatePDF",
        lambda html, dest, options: dest.write(b"pdf"),
    )
    monkeypatch.setattr(
        PdfReportBuilder,
        "_PdfReportBuilder__load_template",
        lambda self, template_name: _FakeFrontTemplate(),
    )

    builder.generate_pdf()
    payload = _CaptureTemplate.captured[-1]
    types = [s["type"] for s in payload["sections"]]

    assert "fit_description" in types
    assert "digital_forensics" in types
    assert "wacz_description" in types
    assert "case_info" in types
    assert "system_artifacts" in types
    assert "acquired_content" in types
