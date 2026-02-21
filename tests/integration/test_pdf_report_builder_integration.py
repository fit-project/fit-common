import importlib.util

import pytest
from pypdf import PdfReader

from fit_common.core.acquisition_type import AcquisitionType
from fit_common.core.pdf_report_builder import PdfReportBuilder, ReportType


def _require_fit_assets() -> None:
    if importlib.util.find_spec("fit_assets") is None:
        pytest.skip("fit_assets package not installed. Install it to run integration tests.")


def _translations() -> dict[str, str]:
    return {
        "DOCUMENT_TITLE": "Document",
        "DOCUMENT_SUBTITLE": "Subtitle",
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
        "TABLE_ROW_DESCRIPTION_PEC_EMAIL": "pec",
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


@pytest.mark.integration
def test_generate_pdf_verify_real_stack(tmp_path):
    _require_fit_assets()

    verify_info = tmp_path / "verify_info.txt"
    verify_info.write_text("verification detail", encoding="utf-8")
    output_name = "verification_report.pdf"

    builder = PdfReportBuilder(
        ReportType.VERIFY,
        translations=_translations(),
        path=str(tmp_path),
        filename=output_name,
        case_info={"name": "Case A"},
    )
    builder.ntp = "2026-02-21"
    builder.verify_result = True
    builder.verify_info_file_path = str(verify_info)

    builder.generate_pdf()

    output_file = tmp_path / output_name
    assert output_file.exists()
    reader = PdfReader(str(output_file))
    assert len(reader.pages) >= 1
    assert not verify_info.exists()


@pytest.mark.integration
def test_generate_pdf_acquisition_real_stack(tmp_path):
    _require_fit_assets()

    (tmp_path / "acquisition.log").write_text("log content", encoding="utf-8")
    (tmp_path / "acquisition.hash").write_text("sha256 abc\n", encoding="latin-1")
    (tmp_path / "whois.txt").write_text("owner example", encoding="utf-8")
    (tmp_path / "video.mp4").write_bytes(b"fake-video")
    (tmp_path / "capture.pcap").write_bytes(b"fake-pcap")
    output_name = "acquisition_report.pdf"

    builder = PdfReportBuilder(
        ReportType.ACQUISITION,
        translations=_translations(),
        path=str(tmp_path),
        filename=output_name,
        case_info={"name": "Case B"},
        screen_recorder_filename="video.mp4",
        packet_capture_filename="capture.pcap",
    )
    builder.acquisition_type = AcquisitionType.WEB
    builder.ntp = "2026-02-21"

    builder.generate_pdf()

    output_file = tmp_path / output_name
    assert output_file.exists()
    reader = PdfReader(str(output_file))
    assert len(reader.pages) >= 1
