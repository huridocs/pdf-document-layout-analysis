from adapters.storage.file_system_repository import FileSystemRepository
from adapters.ml.vgt_model_adapter import VGTModelAdapter
from adapters.ml.fast_trainer_adapter import FastTrainerAdapter
from adapters.infrastructure.pdf_analysis_service_adapter import PDFAnalysisServiceAdapter
from adapters.infrastructure.text_extraction_adapter import TextExtractionAdapter
from adapters.infrastructure.toc_service_adapter import TOCServiceAdapter
from adapters.infrastructure.visualization_service_adapter import VisualizationServiceAdapter
from adapters.infrastructure.ocr_service_adapter import OCRServiceAdapter
from adapters.infrastructure.format_conversion_service_adapter import FormatConversionServiceAdapter
from adapters.infrastructure.markdown_conversion_service_adapter import MarkdownConversionServiceAdapter
from adapters.infrastructure.html_conversion_service_adapter import HtmlConversionServiceAdapter
from adapters.web.fastapi_controllers import FastAPIControllers
from use_cases.pdf_analysis.analyze_pdf_use_case import AnalyzePDFUseCase
from use_cases.pdf_analysis.get_pdf_word_positions import get_pdf_word_positions
from use_cases.text_extraction.extract_text_use_case import ExtractTextUseCase
from use_cases.toc_extraction.extract_toc_use_case import ExtractTOCUseCase
from use_cases.visualization.create_visualization_use_case import CreateVisualizationUseCase
from use_cases.ocr.process_ocr_use_case import ProcessOCRUseCase
from use_cases.markdown_conversion.convert_to_markdown_use_case import ConvertToMarkdownUseCase
from use_cases.html_conversion.convert_to_html_use_case import ConvertToHtmlUseCase


def setup_dependencies():
    file_repository = FileSystemRepository()

    vgt_model_service = VGTModelAdapter()
    fast_model_service = FastTrainerAdapter()

    format_conversion_service = FormatConversionServiceAdapter()
    markdown_conversion_service = MarkdownConversionServiceAdapter()
    html_conversion_service = HtmlConversionServiceAdapter()
    text_extraction_service = TextExtractionAdapter()
    toc_service = TOCServiceAdapter()
    visualization_service = VisualizationServiceAdapter()
    ocr_service = OCRServiceAdapter()

    pdf_analysis_service = PDFAnalysisServiceAdapter(
        vgt_model_service=vgt_model_service,
        fast_model_service=fast_model_service,
        format_conversion_service=format_conversion_service,
        file_repository=file_repository,
    )

    analyze_pdf_use_case = AnalyzePDFUseCase(pdf_analysis_service=pdf_analysis_service, ml_model_service=vgt_model_service)

    extract_text_use_case = ExtractTextUseCase(
        pdf_analysis_service=pdf_analysis_service, text_extraction_service=text_extraction_service
    )

    extract_toc_use_case = ExtractTOCUseCase(pdf_analysis_service=pdf_analysis_service, toc_service=toc_service)

    create_visualization_use_case = CreateVisualizationUseCase(
        pdf_analysis_service=pdf_analysis_service, visualization_service=visualization_service
    )

    process_ocr_use_case = ProcessOCRUseCase(ocr_service=ocr_service, file_repository=file_repository)

    convert_to_markdown_use_case = ConvertToMarkdownUseCase(
        pdf_analysis_service=pdf_analysis_service, markdown_conversion_service=markdown_conversion_service
    )

    convert_to_html_use_case = ConvertToHtmlUseCase(
        pdf_analysis_service=pdf_analysis_service, html_conversion_service=html_conversion_service
    )

    controllers = FastAPIControllers(
        analyze_pdf_use_case=analyze_pdf_use_case,
        extract_text_use_case=extract_text_use_case,
        extract_toc_use_case=extract_toc_use_case,
        create_visualization_use_case=create_visualization_use_case,
        process_ocr_use_case=process_ocr_use_case,
        convert_to_markdown_use_case=convert_to_markdown_use_case,
        convert_to_html_use_case=convert_to_html_use_case,
        file_repository=file_repository,
    )

    return controllers
