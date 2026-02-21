#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


import base64
import os
import tempfile
import zipfile
from enum import Enum, auto
from importlib.resources import files
from typing import Mapping

from jinja2 import Template
from pypdf import PdfReader, PdfWriter
from xhtml2pdf import pisa

from fit_common.core import AcquisitionType, get_version


class ReportType(Enum):
    ACQUISITION = auto()
    VERIFY = auto()


class PdfReportBuilder:
    def __init__(
        self,
        report_type: ReportType,
        translations: Mapping[str, str] | None = None,
        path: str | None = None,
        filename: str | None = None,
        case_info: Mapping[str, object] | None = None,
        screen_recorder_filename: str | None = None,
        packet_capture_filename: str | None = None,
    ) -> None:
        self.__translations = translations
        self.__path = path
        self.__filename = filename
        self.__case_info = case_info or {}
        self.__screen_recorder_filename = screen_recorder_filename
        self.__packet_capture_filename = packet_capture_filename
        self.__report_type = report_type
        self.__temp_dir = tempfile.TemporaryDirectory()
        self.__output_front = os.path.join(self.__temp_dir.name, "front_report.pdf")
        self.__output_content = os.path.join(self.__temp_dir.name, "content_report.pdf")
        self.__acquisition_type = None
        self.__ntp = None
        self.__verify_result = None
        self.__verify_info_file_path = None

    @property
    def ntp(self) -> str | None:
        return self.__ntp

    @ntp.setter
    def ntp(self, ntp: str | None) -> None:
        self.__ntp = ntp

    @property
    def acquisition_type(self) -> AcquisitionType | None:
        return self.__acquisition_type

    @acquisition_type.setter
    def acquisition_type(self, acquisition_type: AcquisitionType | None) -> None:
        self.__acquisition_type = acquisition_type

    @property
    def verify_result(self) -> bool | None:
        return self.__verify_result

    @verify_result.setter
    def verify_result(self, verify_result: bool | None) -> None:
        self.__verify_result = verify_result

    @property
    def verify_info_file_path(self) -> str | None:
        return self.__verify_info_file_path

    @verify_info_file_path.setter
    def verify_info_file_path(self, verify_info_file_path: str | None) -> None:
        self.__verify_info_file_path = verify_info_file_path

    @staticmethod
    def __safe_text(value: object | None) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def generate_pdf(self) -> None:
        logo_path = files("fit_assets.images") / "logo-640x640.png"
        logo_bytes = logo_path.read_bytes()
        logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
        template = self.__load_template("front.html")

        front_page_html = template.render(
            img=f"data:image/png;base64,{logo_base64}",
            document_title=self.__translations["DOCUMENT_TITLE"],
            document_subtitle=self.__translations["DOCUMENT_SUBTITLE"],
            application_short_name=self.__translations["APPLICATION_SHORT_NAME"],
            version=get_version(),
        )

        sections = []

        # FIT Description
        sections.append(
            {
                "title": self.__translations["DOCUMENT_TITLE"],
                "type": "fit_description",
                "content": self.__translations[
                    "SECTION_DESCRIPTION_FIT_APPLICATION"
                ].format(self.__translations["RELEASES_LINK"]),
            }
        )

        if self.__report_type == ReportType.ACQUISITION:
            # Digital Forensics
            sections.append(
                {
                    "title": self.__translations["SECTION_TITLE_DIGITAL_FORENSICS"],
                    "type": "digital_forensics",
                    "description": self.__translations[
                        "SECTION_DESCRIPTION_DIGITAL_FORENSICS"
                    ],
                    "subtitles": {
                        "chain_of_custody": self.__translations[
                            "SECTION_TITLE_CHAIN_OF_CUSTODY"
                        ],
                        "hashes": self.__translations["SECTION_TITLE_HASHES"],
                    },
                    "contents": {
                        "chain_of_custody": self.__translations[
                            "SECTION_DESCRIPTION_CHAIN_OF_CUSTODY"
                        ],
                        "hashes": self.__translations["SECTION_DESCRIPTION_HASHES"],
                    },
                }
            )

        if self.__acquisition_type == AcquisitionType.WEB:
            # Format of the acquired web content (WACZ)
            sections.append(
                {
                    "title": self.__translations["SECTION_TITLE_WACZ"],
                    "type": "wacz_description",
                    "content": self.__translations["SECTION_DESCRIPTION_WACZ"],
                }
            )

        # Case Information
        case_rows = [
            {
                "value": self.__translations["TABLE_ROW_LABEL_CASE"],
                "desc": self.__safe_text(self.__case_info.get("name")) or "N/A",
            },
            {
                "value": self.__translations["TABLE_ROW_LABEL_LAWYER"],
                "desc": self.__safe_text(self.__case_info.get("lawyer_name")) or "N/A",
            },
            {
                "value": self.__translations["TABLE_ROW_LABEL_OPERATOR"],
                "desc": self.__safe_text(self.__case_info.get("operator")) or "N/A",
            },
            {
                "value": self.__translations["TABLE_ROW_LABEL_PROCEEDING"],
                "desc": self.__safe_text(self.__case_info.get("proceeding_type_name"))
                or "N/A",
            },
            {
                "value": self.__translations["TABLE_ROW_LABEL_COURT"],
                "desc": self.__safe_text(self.__case_info.get("courthouse")) or "N/A",
            },
            {
                "value": self.__translations["TABLE_ROW_LABEL_PROCEEDING_NUMBER"],
                "desc": self.__safe_text(self.__case_info.get("proceeding_number"))
                or "N/A",
            },
        ]

        if self.acquisition_type:
            case_rows.append(
                {
                    "value": self.__translations["ACQUISITION_TYPE"],
                    "desc": self.__acquisition_type,
                }
            )

        case_rows.append(
            {"value": self.__translations["ACQUISITION_DATE"], "desc": self.__ntp}
        )
        sections.append(
            {
                "title": self.__translations["SECTION_TITLE_GENERAL_INFORMATION"],
                "type": "case_info",
                "description": "",
                "columns": [
                    self.__translations["TABLE_COLUMN_CASE_INFO"],
                    self.__translations["TABLE_COLUMN_CASE_DATA"],
                ],
                "rows": case_rows,
                "note": self.__safe_text(self.__case_info.get("notes")) or "N/A",
            }
        )

        # Company Logo
        logo = (self.__case_info.get("logo_bin") or "").strip()
        if logo:
            logo = (
                '<div style="padding-bottom: 10px;"><img src="data:image/png;base64,'
                + base64.b64encode(logo).decode("utf-8")
                + '" height="'
                + self.__case_info.get("logo_height", "")
                + '" width="'
                + self.__case_info.get("logo_width", "")
                + '"></div>'
            )
        else:
            logo = "<div></div>"

        if self.__report_type == ReportType.ACQUISITION:
            # System artifacts
            acquisition_files = self._acquisition_files_names()
            file_checks = [
                (
                    "acquisition_report.pdf",
                    self.__translations["TABLE_ROW_DESCRIPTION_REPORT"],
                ),
                (
                    self.__screen_recorder_filename,
                    self.__translations["TABLE_ROW_DESCRIPTION_SCREEN_CAPTURE"],
                ),
                ("acquisition.hash", self.__translations["TABLE_ROW_DESCRIPTION_HASH"]),
                ("acquisition.log", self.__translations["TABLE_ROW_DESCRIPTION_LOG"]),
                (
                    self.__packet_capture_filename,
                    self.__translations["TABLE_ROW_DESCRIPTION_PCAP"],
                ),
                (
                    "caseinfo.json",
                    self.__translations["TABLE_ROW_DESCRIPTION_CASE_INFORMATION"],
                ),
                (
                    "system_info.txt",
                    self.__translations["TABLE_ROW_DESCRIPTION_SYSTEM_INFORMATION"],
                ),
                (
                    "timestamp.tsr",
                    self.__translations["TABLE_ROW_DESCRIPTION_TIMESTAMP_TSR"],
                ),
                (
                    "tsa.crt",
                    self.__translations["TABLE_ROW_DESCRIPTION_TSA_CERTIFICATE"],
                ),
                ("whois.txt", self.__translations["TABLE_ROW_DESCRIPTION_WHOIS"]),
                ("headers.txt", self.__translations["TABLE_ROW_DESCRIPTION_HEADERS"]),
                ("nslookup.txt", self.__translations["TABLE_ROW_DESCRIPTION_NSLOOKUP"]),
                ("server.cer", self.__translations["TABLE_ROW_DESCRIPTION_CER"]),
                (
                    "sslkey.log",
                    self.__translations["TABLE_ROW_DESCRIPTION_SSLKEYLOG"],
                ),
                (
                    "traceroute.txt",
                    self.__translations["TABLE_ROW_DESCRIPTION_TRACEROUTE"],
                ),
            ]

            if self.__eml_filename is not None:
                file_checks.append(
                    (
                        self.__eml_filename,
                        self.__translations["TABLE_ROW_DESCRIPTION_PEC_EMAIL"],
                    ),
                )

            file_rows = [
                {"value": acquisition_files[file], "desc": desc}
                for file, desc in file_checks
                if file in acquisition_files and acquisition_files[file]
            ]

            sections.append(
                {
                    "title": self.__translations["SECTION_TITLE_SYSTEM_ARTIFACTS"],
                    "type": "system_artifacts",
                    "description": self.__translations[
                        "SECTION_DESCRIPTION_SYSTEM_ARTIFACTS"
                    ],
                    "columns": [
                        self.__translations["TABLE_COLUMN_FILE_NAME"],
                        self.__translations["TABLE_COLUMN_FILE_DESCRIPTION"],
                    ],
                    "rows": file_rows,
                    "note": "",
                }
            )

            # Acquired Content
            acquisition_files = self._acquisition_files_names()
            file_checks = [
                (
                    "acquisition_page.png",
                    self.__translations["TABLE_ROW_DESCRIPTION_PAGE_SCREENSHOT"],
                ),
                (
                    "acquisition_page.wacz",
                    self.__translations["TABLE_ROW_DESCRIPTION_WACZ"],
                ),
                (
                    "acquisition_mail.zip",
                    self.__translations["TABLE_ROW_DESCRIPTION_MAIL_ACQUISITION"],
                ),
                (
                    "acquisition.zip",
                    self.__translations["TABLE_ROW_DESCRIPTION_ACQUISITION_ARCHIVE"],
                ),
                (
                    "screenshot.zip",
                    self.__translations["TABLE_ROW_DESCRIPTION_SCREENSHOTS_ARCHIVE"],
                ),
                (
                    "downloads.zip",
                    self.__translations["TABLE_ROW_DESCRIPTION_DOWNLOADS_ARCHIVE"],
                ),
            ]
            file_rows = [
                {"value": acquisition_files[file], "desc": desc}
                for file, desc in file_checks
                if file in acquisition_files and acquisition_files[file]
            ]

            sections.append(
                {
                    "title": self.__translations["SECTION_TITLE_ACQUIRED_CONTENT"],
                    "type": "acquired_content",
                    "description": self.__translations[
                        "SECTION_DESCRIPTION_ACQUIRED_CONTENT"
                    ],
                    "columns": [
                        self.__translations["TABLE_COLUMN_FILE_NAME"],
                        self.__translations["TABLE_COLUMN_FILE_DESCRIPTION"],
                    ],
                    "rows": file_rows,
                    "note": "",
                }
            )

            # hash
            hash_content = self.__hash_reader()
            if hash_content:
                sections.append(
                    {
                        "title": self.__translations[
                            "SECTION_TITLE_INTEGRITY_VERIFICATION"
                        ],
                        "type": "integrity_verification",
                        "description": self.__translations[
                            "SECTION_DESCRIPTION_INTEGRITY_VERIFICATION"
                        ],
                        "content": hash_content,
                    }
                )

            # whois
            whois_content = self.__read_file("whois.txt")
            if whois_content:
                sections.append(
                    {
                        "title": self.__translations[
                            "SECTION_TITLE_DATA_OWNERSHIP_VERIFICATION"
                        ],
                        "type": "whois",
                        "description": self.__translations[
                            "SECTION_DESCRIPTION_DATA_OWNERSHIP_VERIFICATION"
                        ],
                        "content": whois_content,
                    }
                )

            # Screenshots
            screenshot_content = self.__insert_screenshot()
            if screenshot_content:
                sections.append(
                    {
                        "title": self.__translations.get(
                            "SCREENSHOT_LINK_LABEL",
                            self.__translations["SECTION_TITLE_SCREENSHOTS"],
                        ),
                        "type": "screenshot",
                        "description": self.__translations[
                            "SECTION_DESCRIPTION_SCREENSHOTS"
                        ],
                        "content": screenshot_content,
                    }
                )

            # Video
            video_content = self.__insert_video_hyperlink()
            if video_content:
                sections.append(
                    {
                        "title": self.__translations["SECTION_TITLE_VIDEO_ACQUISITION"],
                        "type": "video",
                        "description": self.__translations[
                            "SECTION_DESCRIPTION_VIDEO_ACQUISITION"
                        ],
                        "content": video_content,
                    }
                )

        if self.__report_type == ReportType.VERIFY:
            # Verification report
            verification_result = ""
            if self.__verify_result:
                verification_result = (
                    self.__translations["VERIFI_OK"]
                    if self.__verify_result
                    else self.__translations["VERIFI_KO"]
                )
            info_file = ""
            if self.__verify_info_file_path:
                with open(self.__verify_info_file_path, "r") as f:
                    info_file = f.read()

            sections.append(
                {
                    "title": self.__translations["SECTION_TITLE_VERIFICATION"],
                    "type": "verification_report",
                    "verification_result": verification_result,
                    "content": info_file,
                }
            )

        template = Template(
            (files("fit_assets.templates") / "content.html").read_text(encoding="utf-8")
        )

        content_page_html = template.render(
            title=self.__translations["APPLICATION_SHORT_NAME"],
            document_title=self.__translations["DOCUMENT_TITLE"],
            index=self.__translations["INDEX"],
            sections=sections,
            note=self.__translations["NOTE"],
            logo=logo,
            page=self.__translations["PAGE"],
            of=self.__translations["OF"],
        )

        pdf_options = {
            "page-size": "Letter",
            "margin-top": "1in",
            "margin-right": "1in",
            "margin-bottom": "1in",
            "margin-left": "1in",
        }

        # create pdf front and content, merge them and remove merged files
        with open(self.__output_front, "w+b") as front_result:
            pisa.CreatePDF(front_page_html, dest=front_result, options=pdf_options)

        with open(self.__output_content, "w+b") as content_result:
            pisa.CreatePDF(content_page_html, dest=content_result, options=pdf_options)

        writer = PdfWriter()
        with open(self.__output_front, "rb") as f_front:
            reader_front = PdfReader(f_front)
            for page in reader_front.pages:
                writer.add_page(page)

        with open(self.__output_content, "rb") as f_content:
            reader_content = PdfReader(f_content)
            for page in reader_content.pages:
                writer.add_page(page)

        output_path = os.path.join(self.__path, self.__filename)
        with open(output_path, "wb") as f_out:
            writer.write(f_out)

        if os.path.exists(self.__output_front):
            os.remove(self.__output_front)
        if os.path.exists(self.__output_content):
            os.remove(self.__output_content)
        if self.__verify_info_file_path is not None and os.path.exists(
            self.__verify_info_file_path
        ):
            os.remove(self.__verify_info_file_path)

    def __load_template(self, template: str) -> Template:
        return Template(
            (files("fit_assets.templates") / template).read_text(encoding="utf-8")
        )

    def __read_file(self, filename: str) -> str | None:
        try:
            file_path = os.path.join(self.__path, filename)
            if os.path.getsize(file_path) == 0:
                return None
            with open(file_path, "r") as f:
                content = f.read()
                return content if content.strip() else None
        except (FileNotFoundError, OSError):
            return None

    def __force_wrap(self, text: str, every: int = 80) -> str:
        return "\n".join(text[i : i + every] for i in range(0, len(text), every))

    def __pec_eml_filename(self) -> str | None:
        if not self.__path or not os.path.isdir(self.__path):
            return None

        for entry in os.scandir(self.__path):
            if entry.is_file() and entry.name.lower().endswith(".eml"):
                return entry.name

        return None

    def _acquisition_files_names(self) -> dict[str, str]:
        acquisition_files = {}
        files = [f.name for f in os.scandir(self.__path) if f.is_file()]
        for file in files:
            acquisition_files[file] = file

        file_checks = [
            "acquisition_page.png",
            "acquisition_page.wacz",
            "acquisition_mail.zip",
            "acquisition_report.pdf",
            self.__screen_recorder_filename,
            "acquisition.hash",
            "acquisition.log",
            "acquisition.zip",
            self.__packet_capture_filename,
            "caseinfo.json",
            "headers.txt",
            "nslookup.txt",
            "screenshot.zip",
            "downloads.zip",
            "server.cer",
            "system_info.txt",
            "timestamp.tsr",
            "sslkey.log",
            "traceroute.txt",
            "tsa.crt",
            "whois.txt",
        ]

        for filename in file_checks:
            matching_files = [
                file for file in acquisition_files.values() if file.startswith(filename)
            ]

            if not matching_files:
                acquisition_files.pop(filename, None)
            else:
                actual_file = matching_files[0]
                if self.__is_empty_file(actual_file):
                    acquisition_files[actual_file] = self.__translations[
                        "EMPTY_FILE"
                    ].format(actual_file)

        self.__eml_filename = self.__pec_eml_filename()
        if self.__eml_filename is not None:
            acquisition_files[self.__eml_filename] = self.__eml_filename

        return acquisition_files

    def __is_empty_file(self, filename: str) -> bool:
        path = os.path.join(self.__path, filename)
        return not os.path.isfile(path) or os.path.getsize(path) == 0

    def _zip_files_enum(self) -> str:
        zip_enum = ""
        zip_dir = None
        # getting zip folder and passing file names and dimensions to the template
        for fname in os.listdir(self.__path):
            if fname.endswith(".zip"):
                zip_dir = os.path.join(self.__path, fname)

        if zip_dir:
            zip_folder = zipfile.ZipFile(zip_dir)
            for zip_file in zip_folder.filelist:
                size = zip_file.file_size
                filename = zip_file.filename
                if filename.count(".") > 1:
                    filename = filename.rsplit(".", 1)[0]
                else:
                    pass
                if size > 0:
                    zip_enum += "<p>" + self.__force_wrap(filename, 78) + "</p>"
                    zip_enum += (
                        "<p>" + self.__translations["SIZE"] + str(size) + " bytes</p>"
                    )
                    zip_enum += "<hr>"
        return zip_enum

    def __hash_reader(self) -> str:
        hash_text = ""
        filename = "acquisition.hash"

        if self.__read_file(filename):
            with open(
                os.path.join(
                    self.__path,
                    filename,
                ),
                "r",
                encoding="latin-1",
            ) as f:
                for line in f:
                    hash_text += "<p>" + line + "</p>"

        return hash_text

    def __insert_screenshot(self) -> str:
        screenshot_path = os.path.join(self.__path, "acquisition_page.png")
        if not os.path.isfile(screenshot_path):
            return ""

        # A4 portrait content area with current margins is about 445pt x 692pt.
        # Keep extra room for title/description so the screenshot fits on one page.
        max_width = 430
        max_height = 520
        width, height = self.__read_png_dimensions(screenshot_path)
        img_attributes = 'style="display:block; margin: 0 auto;"'

        if width and height and width > 0 and height > 0:
            scale = min(max_width / width, max_height / height, 1)
            render_width = max(1, int(width * scale))
            render_height = max(1, int(height * scale))
            img_attributes = (
                f'width="{render_width}" height="{render_height}" '
                'style="display:block; margin: 0 auto;"'
            )
        else:
            img_attributes = (
                f'width="{max_width}" height="{max_height}" '
                'style="display:block; margin: 0 auto;"'
            )

        return (
            "<p>"
            '<a href="file://'
            + screenshot_path
            + '">'
            + self.__translations["SCREENSHOT_LINK_LABEL"]
            + '</a></p><p><img src="'
            + screenshot_path
            + '" '
            + img_attributes
            + "></p>"
        )

    @staticmethod
    def __read_png_dimensions(path: str) -> tuple[int | None, int | None]:
        try:
            with open(path, "rb") as f:
                header = f.read(24)
        except OSError:
            return None, None

        if len(header) < 24:
            return None, None
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            return None, None
        if header[12:16] != b"IHDR":
            return None, None

        width = int.from_bytes(header[16:20], "big")
        height = int.from_bytes(header[20:24], "big")
        return width, height

    def __insert_video_hyperlink(self) -> str | None:
        acquisition_files = {}
        files = [f.name for f in os.scandir(self.__path) if f.is_file()]
        for file in files:
            acquisition_files[file] = file

        matching_files = [
            file
            for file in acquisition_files.values()
            if file.startswith(self.__screen_recorder_filename)
        ]

        if matching_files:
            actual_filename = matching_files[0]
            hyperlink = (
                '<a href="file://'
                + os.path.join(self.__path, actual_filename)
                + '">'
                + self.__translations["VIDEO_LINK_LABEL"]
                + "</a>"
            )
        else:
            hyperlink = None

        return hyperlink
