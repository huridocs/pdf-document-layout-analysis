from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment
from ports.services.ml_model_service import MLModelService
from adapters.ml.vgt.ditod import VGTTrainer
from adapters.ml.vgt.get_model_configuration import get_model_configuration
from adapters.ml.vgt.get_most_probable_pdf_segments import get_most_probable_pdf_segments
from adapters.ml.vgt.get_reading_orders import get_reading_orders
from adapters.ml.vgt.get_json_annotations import get_annotations
from adapters.ml.vgt.create_word_grid import create_word_grid, remove_word_grids
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.data.datasets import register_coco_instances
from detectron2.data import DatasetCatalog
from configuration import JSON_TEST_FILE_PATH, IMAGES_ROOT_PATH

configuration = get_model_configuration()
model = VGTTrainer.build_model(configuration)
DetectionCheckpointer(model, save_dir=configuration.OUTPUT_DIR).resume_or_load(configuration.MODEL.WEIGHTS, resume=True)


class VGTModelAdapter(MLModelService):

    def _register_data(self) -> None:
        try:
            DatasetCatalog.remove("predict_data")
        except KeyError:
            pass

        register_coco_instances("predict_data", {}, JSON_TEST_FILE_PATH, IMAGES_ROOT_PATH)

    def predict_document_layout(self, pdf_images: list[PdfImages]) -> list[PdfSegment]:
        create_word_grid([pdf_images_obj.pdf_features for pdf_images_obj in pdf_images])
        get_annotations(pdf_images)

        self._register_data()
        VGTTrainer.test(configuration, model)

        predicted_segments = get_most_probable_pdf_segments("doclaynet", pdf_images, False)

        PdfImages.remove_images()
        remove_word_grids()

        return get_reading_orders(pdf_images, predicted_segments)

    def predict_layout_fast(self, pdf_images: list[PdfImages]) -> list[PdfSegment]:
        raise NotImplementedError("Fast prediction should be handled by FastTrainerAdapter")
