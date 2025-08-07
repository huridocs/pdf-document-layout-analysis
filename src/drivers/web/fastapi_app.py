import torch
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from adapters.web.fastapi_controllers import FastAPIControllers
from catch_exceptions import catch_exceptions
from configuration import service_logger


def create_app(controllers: FastAPIControllers) -> FastAPI:
    service_logger.info(f"Is PyTorch using GPU: {torch.cuda.is_available()}")

    app = FastAPI()

    app.get("/")(controllers.root)
    app.get("/info")(controllers.info)
    app.get("/error")(controllers.error)

    app.post("/")(catch_exceptions(controllers.analyze_pdf))
    app.post("/save_xml/{xml_file_name}")(catch_exceptions(controllers.analyze_and_save_xml))
    app.get("/get_xml/{xml_file_name}", response_class=PlainTextResponse)(catch_exceptions(controllers.get_xml_by_name))

    app.post("/toc")(catch_exceptions(controllers.get_toc_endpoint))
    app.post("/toc_legacy_uwazi_compatible")(catch_exceptions(controllers.toc_legacy_uwazi_compatible))

    app.post("/text")(catch_exceptions(controllers.get_text_endpoint))
    app.post("/visualize")(catch_exceptions(controllers.get_visualization_endpoint))
    app.post("/markdown", response_model=None)(catch_exceptions(controllers.convert_to_markdown_endpoint))
    app.post("/html", response_model=None)(catch_exceptions(controllers.convert_to_html_endpoint))
    app.post("/ocr")(catch_exceptions(controllers.ocr_pdf_sync))

    return app
