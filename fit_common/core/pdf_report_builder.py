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
        translations=None,
        path=None,
        filename=None,
        case_info=None,
        screen_recorder_filename=None,
        packet_capture_filename=None,
    ):
        self.__translations = translations
        self.__path = path
        self.__filename = filename
        self.__case_info = case_info
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
    def ntp(self):
        return self.__ntp

    @ntp.setter
    def ntp(self, ntp):
        self.__ntp = ntp

    @property
    def acquisition_type(self):
        return self.__acquisition_type

    @acquisition_type.setter
    def acquisition_type(self, acquisition_type):
        self.__acquisition_type = acquisition_type

    @property
    def verify_result(self):
        return self.__verify_result

    @verify_result.setter
    def verify_result(self, verify_result):
        self.__verify_result = verify_result

    @property
    def verify_info_file_path(self):
        return self.__verify_info_file_path

    @verify_info_file_path.setter
    def verify_info_file_path(self, verify_info_file_path):
        self.__verify_info_file_path = verify_info_file_path

    def generate_pdf(self):
        logo_path = files("fit_assets.images") / "logo-640x640.png"
        logo_bytes = logo_path.read_bytes()
        logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
        template = self.__load_template("front.html")

        front_page_html = template.render(
            img=f"data:image/png;base64,{logo_base64}",
            t1=self.__translations["T1"],
            title=self.__translations["TITLE"],
            report=self.__translations["REPORT"],
            version=get_version(),
        )

        sections = []

        # FIT Description
        sections.append(
            {
                "title": self.__translations["T1"],
                "type": "fit_description",
                "content": self.__translations["DESCRIPTION"].format(
                    self.__translations["RELEASES_LINK"]
                ),
            }
        )

        if self.__report_type == ReportType.ACQUISITION:
            # Digital Forensics
            sections.append(
                {
                    "title": self.__translations["T4"],
                    "type": "digital_forensics",
                    "description": self.__translations["T4DESCR"],
                    "subtitles": {
                        "cc": self.__translations["TITLECC"],
                        "h": self.__translations["TITLEH"],
                    },
                    "contents": {
                        "cc": self.__translations["CCDESCR"],
                        "h": self.__translations["HDESCR"],
                    },
                }
            )

        if self.__acquisition_type == AcquisitionType.WEB:
            # Format of the acquired web content (WACZ)
            sections.append(
                {
                    "title": self.__translations["WACZ_TITLE"],
                    "type": "wacz_description",
                    "content": self.__translations["WACZ_DESCRIPTION"],
                }
            )

        # Case Information
        case_rows = [
            {
                "value": self.__translations["CASE"],
                "desc": self.__case_info.get("name", "").strip() or "N/A",
            },
            {
                "value": self.__translations["LAWYER"],
                "desc": self.__case_info.get("lawyer_name", "").strip() or "N/A",
            },
            {
                "value": self.__translations["OPERATOR"],
                "desc": self.__case_info.get("operator", "").strip() or "N/A",
            },
            {
                "value": self.__translations["PROCEEDING"],
                "desc": str(self.__case_info.get("proceeding_type_name", "")).strip()
                or "N/A",
            },
            {
                "value": self.__translations["COURT"],
                "desc": self.__case_info.get("courthouse", "").strip() or "N/A",
            },
            {
                "value": self.__translations["NUMBER"],
                "desc": self.__case_info.get("proceeding_number", "").strip() or "N/A",
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
                "title": self.__translations["T2"],
                "type": "case_info",
                "description": "",
                "columns": [
                    self.__translations["CASEINFO"],
                    self.__translations["CASEDATA"],
                ],
                "rows": case_rows,
                "note": self.__case_info.get("notes", "").strip() or "N/A",
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
            # Acquisition Files
            acquisition_files = self._acquisition_files_names()
            file_checks = [
                (
                    self.__screen_recorder_filename,
                    self.__translations["AVID"],
                ),
                ("acquisition.hash", self.__translations["HASHD"]),
                ("acquisition.log", self.__translations["LOGD"]),
                (
                    self.__packet_capture_filename,
                    self.__translations["PCAPD"],
                ),
                ("acquisition.zip", self.__translations["ZIPD"]),
                ("whois.txt", self.__translations["WHOISD"]),
                ("headers.txt", self.__translations["HEADERSD"]),
                ("nslookup.txt", self.__translations["NSLOOKUPD"]),
                ("server.cer", self.__translations["CERD"]),
                ("sslkey.log", self.__translations["SSLKEYD"]),
                ("traceroute.txt", self.__translations["TRACEROUTED"]),
            ]

            file_rows = [
                {"value": acquisition_files[file], "desc": desc}
                for file, desc in file_checks
                if file in acquisition_files and acquisition_files[file]
            ]

            sections.append(
                {
                    "title": self.__translations["T5"],
                    "type": "file_info",
                    "description": self.__translations["T5DESCR"],
                    "columns": [
                        self.__translations["NAME"],
                        self.__translations["DESCR"],
                    ],
                    "rows": file_rows,
                    "note": "",
                }
            )

            # ZIP Content
            zip_enum = self._zip_files_enum()
            if zip_enum:
                sections.append(
                    {
                        "title": self.__translations["T7"],
                        "type": "zip_content",
                        "description": self.__translations["T7DESCR"],
                        "content": zip_enum,
                    }
                )

            # hash
            hash_content = self.__hash_reader()
            if hash_content:
                sections.append(
                    {
                        "title": self.__translations["T6"],
                        "type": "hash",
                        "description": self.__translations["T6DESCR"],
                        "content": hash_content,
                    }
                )

            # whois
            whois_content = self.__read_file("whois.txt")
            if whois_content:
                sections.append(
                    {
                        "title": self.__translations["T3"],
                        "type": "whois",
                        "description": self.__translations["T3DESCR"],
                        "content": whois_content,
                    }
                )

            # Screenshots
            screenshot_content = self.__insert_screenshot()
            if screenshot_content:
                sections.append(
                    {
                        "title": self.__translations["T8"],
                        "type": "screenshot",
                        "description": self.__translations["T8DESCR"],
                        "content": screenshot_content,
                    }
                )

            # Video
            video_content = self.__insert_video_hyperlink()
            if video_content:
                sections.append(
                    {
                        "title": self.__translations["T9"],
                        "type": "video",
                        "description": self.__translations["T9DESCR"],
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
                    "title": self.__translations["VERIFICATION"],
                    "type": "verification_report",
                    "verification_result": verification_result,
                    "content": info_file,
                }
            )

        template = Template(
            (files("fit_assets.templates") / "content.html").read_text(encoding="utf-8")
        )

        content_page_html = template.render(
            title=self.__translations["TITLE"],
            t1=self.__translations["T1"],
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

    def __load_template(self, template) -> Template:
        return Template(
            (files("fit_assets.templates") / template).read_text(encoding="utf-8")
        )

    def __read_file(self, filename):
        try:
            file_path = os.path.join(self.__path, filename)
            if os.path.getsize(file_path) == 0:
                return None
            with open(file_path, "r") as f:
                content = f.read()
                return content if content.strip() else None
        except (FileNotFoundError, OSError):
            return None
        except FileNotFoundError:
            return None
        except FileNotFoundError:
            return None

    def __force_wrap(self, text, every=80):
        return "\n".join(text[i : i + every] for i in range(0, len(text), every))

    def _acquisition_files_names(self):
        acquisition_files = {}
        files = [f.name for f in os.scandir(self.__path) if f.is_file()]
        for file in files:
            acquisition_files[file] = file

        file_checks = [
            self.__screen_recorder_filename,
            "acquisition.hash",
            "acquisition.log",
            self.__packet_capture_filename,
            "acquisition.zip",
            "whois.txt",
            "headers.txt",
            "nslookup.txt",
            "server.cer",
            "sslkey.log",
            "traceroute.txt",
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

        return acquisition_files

    def __is_empty_file(self, filename):
        path = os.path.join(self.__path, filename)
        return not os.path.isfile(path) or os.path.getsize(path) == 0

    def _zip_files_enum(self):
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

    def __hash_reader(self):
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

    def __insert_screenshot(self):
        screenshot_text = ""
        main_screenshot = ""
        screenshots_path = os.path.join(self.__path, "screenshot")
        full_screenshot_path = os.path.join(self.__path, "screenshot", "full_page")

        if os.path.isdir(screenshots_path):
            main_screenshot_file = os.path.join(self.__path, "screenshot.png")

            if os.path.isdir(full_screenshot_path):
                url_folder = [
                    file
                    for file in os.listdir(full_screenshot_path)
                    if os.path.isdir(os.path.join(full_screenshot_path, file))
                ]

                if url_folder:
                    full_screenshot_path = os.path.join(
                        full_screenshot_path, url_folder[0]
                    )

                images = os.listdir(full_screenshot_path)
                main_screenshot = os.path.join(full_screenshot_path, images[0])

            files = os.listdir(screenshots_path)
            for file in files:
                path = os.path.join(self.__path, "screenshot", file)
                if os.path.isfile(path):
                    if "full_page_" not in os.path.basename(file):
                        screenshot_text += (
                            "<p>"
                            '<a href="file://'
                            + path
                            + '">'
                            + "Screenshot"
                            + os.path.basename(file)
                            + '</a><br><img src="'
                            + path
                            + '"></p><br><br>'
                        )

            # main full page screenshot
            screenshot_text += (
                "<p>"
                '<a href="file://'
                + main_screenshot_file
                + '">'
                + self.__translations["COMPLETE_SCREENSHOT"]
                + '</a><br><img src="'
                + main_screenshot
                + '"></p>'
            )

        return screenshot_text

    def __insert_video_hyperlink(self):
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
                + self.__translations["VIDEO_LINK"]
                + "</a>"
            )
        else:
            hyperlink = None

        return hyperlink
