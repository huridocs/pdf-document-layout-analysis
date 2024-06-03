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

            self.assertEqual(200, results.status_code)

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
