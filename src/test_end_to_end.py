import requests
from unittest import TestCase
from configuration import ROOT_PATH


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

            results_dict = results.json()
            expected_content = "RESOLUCIÓN DE LA CORTE INTERAMERICANA DE DERECHOS HUMANOS DEL 29 DE JULIO DE 1991"
            self.assertEqual(200, results.status_code)
            self.assertEqual(expected_content, results_dict[0]["text"])
            self.assertEqual(157, results_dict[0]["left"])
            self.assertEqual(105, results_dict[0]["top"])
            self.assertEqual(283, results_dict[0]["width"])
            self.assertEqual(36, results_dict[0]["height"])
            self.assertEqual(1, results_dict[0]["page_number"])
            self.assertEqual(595, results_dict[0]["page_width"])
            self.assertEqual(842, results_dict[0]["page_height"])
            self.assertEqual("SECTION_HEADER", results_dict[0]["type"])

    def test_error_file_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/error.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}/fast", files=files)

            self.assertEqual(422, results.status_code)

    def test_blank_pdf_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/blank.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}/fast", files=files)

            self.assertEqual(200, results.status_code)
            self.assertEqual(0, len(results.json()))

    def test_segmentation_some_empty_pages_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/some_empty_pages.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}/fast", files=files)

            self.assertEqual(200, results.status_code)
            self.assertEqual(2, len(results.json()))

    def test_image_pdfs_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/image.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}/fast", files=files)

            self.assertEqual(200, results.status_code)
            self.assertEqual(0, len(results.json()))

    def test_regular_pdf_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/regular.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}/fast", files=files)

            self.assertEqual(200, results.status_code)

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

            results = requests.post(f"{self.service_url}/fast", files=files)

            self.assertEqual(200, results.status_code)

    def test_chinese_fast(self):
        with open(f"{ROOT_PATH}/test_pdfs/chinese.pdf", "rb") as stream:
            files = {"file": stream}

            results = requests.post(f"{self.service_url}/fast", files=files)

            self.assertEqual(200, results.status_code)
