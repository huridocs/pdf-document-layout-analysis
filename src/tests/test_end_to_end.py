from pathlib import Path
import requests
from unittest import TestCase
from configuration import ROOT_PATH

SRC_PATH = Path(__file__).parent.parent.parent


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5060"

    def test_info(self):
        results = requests.get(f"{self.service_url}/info")

        self.assertEqual(200, results.status_code)
        self.assertIn("ko", results.json()["supported_languages"])
        self.assertIn("kor-vert", results.json()["supported_languages"])
        self.assertIn("ru", results.json()["supported_languages"])
        self.assertIn("el", results.json()["supported_languages"])

    def test_error_file(self):
        with open(f"{ROOT_PATH}/test_pdfs/error.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}", files=files)

            self.assertEqual(422, results.status_code)

    def test_blank_pdf(self):
        with open(f"{ROOT_PATH}/test_pdfs/blank.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}", files=files)

            self.assertEqual(200, results.status_code)
            self.assertEqual(0, len(results.json()))

    def test_segmentation_some_empty_pages(self):
        with open(f"{ROOT_PATH}/test_pdfs/some_empty_pages.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}", files=files)

            self.assertEqual(200, results.status_code)
            self.assertEqual(2, len(results.json()))

    def test_image_pdfs(self):
        with open(f"{ROOT_PATH}/test_pdfs/image.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}", files=files)

            self.assertEqual(200, results.status_code)

    def test_regular_pdf(self):
        with open(f"{ROOT_PATH}/test_pdfs/regular.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}", files=files)

            results_list = results.json()
            expected_content = "RESOLUCIÓN DE LA CORTE INTERAMERICANA DE DERECHOS HUMANOS DEL 29 DE JULIO DE 1991"
            self.assertEqual(200, results.status_code)
            self.assertEqual(expected_content, results_list[0]["text"])
            self.assertEqual(157, results_list[0]["left"])
            self.assertEqual(105, results_list[0]["top"])
            self.assertEqual(282, results_list[0]["width"])
            self.assertEqual(36, results_list[0]["height"])
            self.assertEqual(1, results_list[0]["page_number"])
            self.assertEqual(595, results_list[0]["page_width"])
            self.assertEqual(842, results_list[0]["page_height"])
            self.assertEqual("Section header", results_list[0]["type"])

    def test_error_file_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/error.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}

            results = requests.post(f"{self.service_url}", files=files, data=data)

            self.assertEqual(422, results.status_code)

    def test_blank_pdf_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/blank.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}

            results = requests.post(f"{self.service_url}", files=files, data=data)

            self.assertEqual(200, results.status_code)
            self.assertEqual(0, len(results.json()))

    def test_segmentation_some_empty_pages_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/some_empty_pages.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}

            results = requests.post(f"{self.service_url}", files=files, data=data)

            self.assertEqual(200, results.status_code)
            self.assertEqual(2, len(results.json()))

    def test_image_pdfs_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/image.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}

            results = requests.post(f"{self.service_url}", files=files, data=data)

            self.assertEqual(200, results.status_code)
            self.assertEqual(0, len(results.json()))

    def test_regular_pdf_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/regular.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}
            results = requests.post(f"{self.service_url}", files=files, data=data)

        results_list = results.json()
        expected_content = "RESOLUCIÓN DE LA CORTE INTERAMERICANA DE DERECHOS HUMANOS"
        self.assertEqual(200, results.status_code)
        self.assertEqual(expected_content, results_list[0]["text"])
        self.assertEqual(157, results_list[0]["left"])
        self.assertEqual(106, results_list[0]["top"])
        self.assertEqual(278, results_list[0]["width"])
        self.assertEqual(24, results_list[0]["height"])
        self.assertEqual(1, results_list[0]["page_number"])
        self.assertEqual(595, results_list[0]["page_width"])
        self.assertEqual(842, results_list[0]["page_height"])
        self.assertEqual("Section header", results_list[0]["type"])

    def test_save_xml_fast(self):
        xml_name = "test_fast.xml"
        with open(f"{ROOT_PATH}/test_pdfs/regular.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}
            requests.post(f"{self.service_url}/save_xml/{xml_name}", files=files, data=data)

        result_xml = requests.get(f"{self.service_url}/get_xml/{xml_name}")
        self.assertEqual(200, result_xml.status_code)
        self.assertIsNotNone(result_xml.text)

    def test_save_xml(self):
        xml_name = "test.xml"
        with open(f"{ROOT_PATH}/test_pdfs/regular.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "False"}
            requests.post(f"{self.service_url}/save_xml/{xml_name}", files=files, data=data)

        result_xml = requests.get(f"{self.service_url}/get_xml/{xml_name}")
        self.assertEqual(200, result_xml.status_code)
        self.assertIsNotNone(result_xml.text)

    def test_korean(self):
        with open(f"{ROOT_PATH}/test_pdfs/korean.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}", files=files)

            self.assertEqual(200, results.status_code)

    def test_chinese(self):
        with open(f"{ROOT_PATH}/test_pdfs/chinese.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}", files=files)

            self.assertEqual(200, results.status_code)

    def test_korean_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/korean.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}

            results = requests.post(f"{self.service_url}", files=files, data=data)

            self.assertEqual(200, results.status_code)

    def test_chinese_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/chinese.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}

            results = requests.post(f"{self.service_url}", files=files, data=data)

            self.assertEqual(200, results.status_code)

    def test_toc(self):
        with open(f"{ROOT_PATH}/test_pdfs/toc-test.pdf", "rb") as stream:
            files = {"file": stream}

            response = requests.post(f"{self.service_url}/toc", files=files)

            response_json = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_json), 5)
            self.assertEqual(response_json[0]["label"], "TEST")
            self.assertEqual(response_json[0]["indentation"], 0)
            self.assertEqual(response_json[-1]["label"], "C. TITLE LONGER")
            self.assertEqual(response_json[-1]["indentation"], 2)

    def test_word_positions(self):
        with open(f"{ROOT_PATH}/test_pdfs/regular.pdf", "rb") as stream:
            files = {"file": stream}

            response = requests.post(f"{self.service_url}/word_positions", files=files)

            response_json = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertGreater(len(response_json), 50)

            page_numbers = set(word["page_number"] for word in response_json)
            self.assertEqual(len(page_numbers), 2)

    def test_toc_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/toc-test.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}

            response = requests.post(f"{self.service_url}/toc", files=files, data=data)

            response_json = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_json), 5)
            self.assertEqual(response_json[0]["label"], "TEST")
            self.assertEqual(response_json[0]["indentation"], 0)
            self.assertEqual(response_json[-1]["label"], "C. TITLE LONGER")
            self.assertEqual(response_json[-1]["indentation"], 2)

    def test_toc_from_xml(self):
        import json

        pdf_path = f"{ROOT_PATH}/test_pdfs/toc-test.pdf"
        xml_path = f"{ROOT_PATH}/test_pdfs/toc-test.xml"

        with open(pdf_path, "rb") as stream:
            files = {"file": stream}
            analyze_response = requests.post(f"{self.service_url}", files=files)
            segments = analyze_response.json()

        files = [
            ("segment_boxes", (None, json.dumps(segments))),
            ("file", open(xml_path, "rb")),
        ]
        response = requests.post(f"{self.service_url}/toc_from_xml", files=files)

        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json), 5)
        self.assertEqual(response_json[0]["label"], "TEST")
        self.assertEqual(response_json[0]["indentation"], 0)
        self.assertEqual(response_json[-1]["label"], "C. TITLE LONGER")
        self.assertEqual(response_json[-1]["indentation"], 2)

    def test_text_extraction(self):
        with open(f"{ROOT_PATH}/test_pdfs/test.pdf", "rb") as stream:
            files = {"file": stream}

            response = requests.post(f"{self.service_url}/text", files=files)

            response_json = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json.split()[0], "Document")
            self.assertEqual(response_json.split()[1], "Big")
            self.assertEqual(response_json.split()[-1], "TEXT")

    def test_text_extraction_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/test.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"fast": "True"}

            response = requests.post(f"{self.service_url}/text", files=files, data=data)

            response_json = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json.split()[0], "Document")
            self.assertEqual(response_json.split()[1], "Big")
            self.assertEqual(response_json.split()[-1], "TEXT")

    def test_table_extraction(self):
        with open(f"{ROOT_PATH}/test_pdfs/table.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"parse_tables_and_math": "true"}

            response = requests.post(f"{self.service_url}", files=files, data=data)

            response_json = response.json()
            table_html = response_json[0]["text"]

            parts = table_html.split("<td>")
            values = []
            for part in parts[1:]:
                value = part.split("</td>")[0]
                values.append(value)

            col1, col2, data_1a, data_1b, data_2a, data_2b = values

            self.assertEqual(response.status_code, 200)
            self.assertIn("Column 1", col1)
            self.assertIn("Column 2", col2)
            self.assertIn("Data 1A", data_1a)
            self.assertIn("Data 1B", data_1b)
            self.assertIn("Data 2A", data_2a)
            self.assertIn("Data 2B", data_2b)

    def test_formula_extraction(self):
        with open(f"{ROOT_PATH}/test_pdfs/formula.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"parse_tables_and_math": "true"}

            response = requests.post(f"{self.service_url}", files=files, data=data)

            response_json = response.json()
            formula_text = response_json[1]["text"]
            self.assertEqual(response.status_code, 200)
            self.assertIn("E_{p r i o r}", formula_text)
            self.assertIn("(\\Theta)\\", formula_text)

    def test_ocr_english(self):
        with open(Path(ROOT_PATH, "test_pdfs", "ocr-sample-english.pdf"), "rb") as stream:
            files = {"file": stream}
            result_ocr = requests.post(f"{self.service_url}/ocr", files=files)
            files = {"file": result_ocr.content}
            results = requests.post(f"{self.service_url}", files=files)

        results_list = results.json()
        self.assertEqual(200, results.status_code)
        self.assertEqual(1, len(results_list))
        self.assertEqual("Test  text  OCR", results_list[0]["text"])
        self.assertEqual(248, results_list[0]["left"])
        self.assertEqual(264, results_list[0]["top"])
        self.assertEqual(313, results_list[0]["width"])
        self.assertEqual(50, results_list[0]["height"])
        self.assertEqual(1, results_list[0]["page_number"])
        self.assertEqual(842, results_list[0]["page_width"])
        self.assertEqual(595, results_list[0]["page_height"])
        self.assertEqual("Section header", results_list[0]["type"])

    def test_ocr_pdf_with_text(self):
        with open(Path(ROOT_PATH, "test_pdfs", "ocr-sample-already-ocred.pdf"), "rb") as stream:
            files = {"file": stream}
            result_ocr = requests.post(f"{self.service_url}/ocr", files=files)
            files = {"file": result_ocr.content}
            results = requests.post(f"{self.service_url}", files=files)

        results_list = results.json()
        self.assertEqual(200, results.status_code)
        self.assertEqual(2, len(results_list))
        self.assertEqual("This  is  some  real  text", results_list[0]["text"])
        self.assertEqual("Text", results_list[0]["type"])
        self.assertEqual("This  is  some  text  in  an  image", results_list[1]["text"])
        self.assertEqual("Text", results_list[1]["type"])

    def test_ocr_failing(self):
        with open(Path(ROOT_PATH, "test_pdfs", "not_a_pdf.pdf"), "rb") as stream:
            files = {"file": stream}
            result_ocr = requests.post(f"{self.service_url}/ocr", files=files)

        self.assertEqual(500, result_ocr.status_code)

    def test_html_extraction(self):
        with open(f"{ROOT_PATH}/test_pdfs/regular.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}/html", files=files)

        result = results.json()

        span_elements = [
            "<span id='page-1-0'></span>",
            "<span id='page-1-1'></span>",
            "<span id='page-1-2'></span>",
            "<span id='page-1-3'></span>",
            "<span id='page-1-4'></span>",
            "<span id='page-1-8'></span>",
            "<span id='page-1-11'></span>",
            "<span id='page-1-12'></span>",
            "<span id='page-1-13'></span>",
        ]

        heading_elements = [
            "<h4><b>RESOLUCIÓN DE LA</b> <b>CORTE INTERAMERICANA DE DERECHOS HUMANOS</b> <b>DEL 29 DE JULIO DE 1991</b></h4>",
            "<h4><b>MEDIDAS PROVISIONALES SOLICITADAS POR LA COMISIÓN</b> <b>INTERAMERICANA DE DERECHOS HUMANOS</b> <b>RESPECTO DE GUATEMALA</b></h4>",
            "<h4><b>CASO CHUNIMA</b></h4>",
            "<h4><b>LA CORTE INTERAMERICANA DE DERECHOS HUMANOS,</b></h4>",
            "<h4><b>VISTOS:</b></h4>",
            "<h4><b>CONSIDERANDO:</b></h4>",
            "<h4><b>POR TANTO:</b></h4>",
            "<h4><b>LA CORTE INTERAMERICANA DE DERECHOS HUMANOS,</b></h4>",
            "<h4><b>RESUELVE:</b></h4>",
        ]

        bold_elements = [
            "<b>RESOLUCIÓN DE LA</b>",
            "<b>CORTE INTERAMERICANA DE DERECHOS HUMANOS</b>",
            "<b>DEL 29 DE JULIO DE 1991</b>",
            "<b>MEDIDAS PROVISIONALES SOLICITADAS POR LA COMISIÓN</b>",
            "<b>INTERAMERICANA DE DERECHOS HUMANOS</b>",
            "<b>RESPECTO DE GUATEMALA</b>",
            "<b>CASO CHUNIMA</b>",
            "<b>LA CORTE INTERAMERICANA DE DERECHOS HUMANOS,</b>",
            "<b>VISTOS:</b>",
            "<b>CONSIDERANDO:</b>",
            "<b>POR TANTO:</b>",
            "<b>LA CORTE INTERAMERICANA DE DERECHOS HUMANOS,</b>",
            "<b>RESUELVE:</b>",
        ]

        self.assertEqual(200, results.status_code)

        for span_element in span_elements:
            self.assertIn(span_element, result)

        for heading_element in heading_elements:
            self.assertIn(heading_element, result)

        for bold_element in bold_elements:
            self.assertIn(bold_element, result)

    def test_markdown_extraction(self):
        with open(f"{ROOT_PATH}/test_pdfs/regular.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}/markdown", files=files)

        heading_elements = [
            "#### **RESOLUCIÓN DE LA** **CORTE INTERAMERICANA DE DERECHOS HUMANOS** **DEL 29 DE JULIO DE 1991**\n\n",
            "#### **MEDIDAS PROVISIONALES SOLICITADAS POR LA COMISIÓN** **INTERAMERICANA DE DERECHOS HUMANOS** **RESPECTO DE GUATEMALA**\n\n",
            "#### **CASO CHUNIMA**\n\n",
            "#### **LA CORTE INTERAMERICANA DE DERECHOS HUMANOS,**\n\n",
            "#### **VISTOS:**\n\n",
            "#### **CONSIDERANDO:**\n\n",
            "#### **POR TANTO:**\n\n",
            "#### **LA CORTE INTERAMERICANA DE DERECHOS HUMANOS,**\n\n",
            "#### **RESUELVE:**\n\n",
        ]

        result = results.json()

        self.assertEqual(200, results.status_code)

        for heading_element in heading_elements:
            self.assertIn(heading_element, result)
