from unittest import TestCase

import requests

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
            self.assertEqual(0, len(results.json()))


