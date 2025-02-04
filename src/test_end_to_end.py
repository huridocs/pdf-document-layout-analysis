from pathlib import Path

import requests
from unittest import TestCase
from configuration import ROOT_PATH, SRC_PATH


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5060"

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
            data = {"extraction_format": "markdown"}

            response = requests.post(f"{self.service_url}", files=files, data=data)

            response_json = response.json()
            table_text = response_json[0]["text"]
            self.assertEqual(response.status_code, 200)
            self.assertIn("**Column 1**", table_text.split("\n")[0])
            self.assertIn("**Column 2**", table_text.split("\n")[0])
            self.assertIn("Data 1A", table_text.split("\n")[2])
            self.assertIn("Data 2B", table_text.split("\n")[3])

    def test_formula_extraction(self):
        with open(f"{ROOT_PATH}/test_pdfs/formula.pdf", "rb") as stream:
            files = {"file": stream}
            data = {"extraction_format": "latex"}

            response = requests.post(f"{self.service_url}", files=files, data=data)

            response_json = response.json()
            formula_text = response_json[1]["text"]
            self.assertEqual(response.status_code, 200)
            self.assertIn("E_{_{v r i o r}}", formula_text)
            self.assertIn("-\\ \\Theta||", formula_text)

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
