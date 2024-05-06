import pickle
import tempfile
import uuid
from os.path import join
from pathlib import Path
from typing import AnyStr

from data_model.SegmentBox import SegmentBox
from ditod.VGTTrainer import VGTTrainer
from get_json_annotations import get_annotations
from get_most_probable_pdf_segments import get_most_probable_pdf_segments
from src.PdfImages import PdfImages
from src.configuration import service_logger, JSON_TEST_FILE_PATH, IMAGES_ROOT_PATH
from src.create_word_grid import create_word_grid, remove_word_grids

from detectron2.data import DatasetCatalog
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.config import get_cfg
from detectron2.engine import default_argument_parser, default_setup, launch
from detectron2.data.datasets import register_coco_instances
from detectron2.data import DatasetCatalog


with open("model_configuration/doclaynet_configuration.pickle", mode="rb") as file:
    configuration = pickle.load(file)

model = VGTTrainer.build_model(configuration)
DetectionCheckpointer(model, save_dir=configuration.OUTPUT_DIR).resume_or_load(configuration.MODEL.WEIGHTS, resume=True)


def get_file_path(file_name, extension):
    return join(tempfile.gettempdir(), file_name + "." + extension)


def pdf_content_to_pdf_path(file_content):
    file_id = str(uuid.uuid1())

    pdf_path = Path(get_file_path(file_id, "pdf"))
    pdf_path.write_bytes(file_content)

    return pdf_path


def register_data():
    try:
        DatasetCatalog.remove("predict_data")
    except KeyError:
        pass

    register_coco_instances(
        "predict_data",
        {},
        JSON_TEST_FILE_PATH,
        IMAGES_ROOT_PATH
    )


def predict_doclaynet():
    register_data()
    VGTTrainer.test(configuration, model)


def analyze_pdf(file: AnyStr):
    pdf_path = pdf_content_to_pdf_path(file)
    service_logger.info(f'Creating PDF images')
    pdf_images_list: list[PdfImages] = [PdfImages.from_pdf_path(pdf_path)]
    create_word_grid([pdf_images.pdf_features for pdf_images in pdf_images_list])
    get_annotations(pdf_images_list)
    predict_doclaynet()
    remove_files()
    predicted_segments = get_most_probable_pdf_segments("doclaynet", pdf_images_list, False)
    return [SegmentBox.from_pdf_segment(pdf_segment).to_dict() for pdf_segment in predicted_segments]


def remove_files():
    PdfImages.remove_images()
    remove_word_grids()
