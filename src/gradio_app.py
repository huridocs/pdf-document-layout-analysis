import gradio as gr
import json
import requests
import os
import tempfile
import base64

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5060")


# Helper function to make API calls
def call_api(endpoint: str, files: dict = None, data: dict = None, method: str = "POST"):
    """Make API call to the FastAPI backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=600)
        else:
            response = requests.post(url, files=files, data=data, timeout=60000)

        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f"API call failed: {str(e)}")


def get_system_info():
    """Get system information"""
    try:
        response = call_api("/info", method="GET")
        info_dict = response.json()
        return json.dumps(info_dict, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_pdf(pdf_file: str, fast_mode: bool = False, parse_tables_and_math: bool = False):
    """Analyze PDF and return structured layout information"""
    try:
        if pdf_file is None:
            return "Error: No PDF file provided", ""

        with open(pdf_file, "rb") as f:
            files = {"file": f}
            data = {"fast": str(fast_mode).lower(), "parse_tables_and_math": str(parse_tables_and_math).lower()}
            response = call_api("/", files=files, data=data)

        result = response.json()

        # Format results
        summary = "✓ Analysis complete!\n"
        summary += f"Found {len(result)} segments in the document.\n"

        # Count different types
        type_counts = {}
        for segment in result:
            seg_type = segment.get("type", "unknown")
            type_counts[seg_type] = type_counts.get(seg_type, 0) + 1

        summary += "\nSegment types:\n"
        for seg_type, count in sorted(type_counts.items()):
            summary += f"  - {seg_type}: {count}\n"

        detailed_json = json.dumps(result, indent=2)

        return summary, detailed_json
    except Exception as e:
        return f"Error: {str(e)}", ""


def extract_text(
    pdf_file: str,
    fast_mode: bool = False,
    caption: bool = True,
    footnote: bool = True,
    formula: bool = True,
    list_item: bool = True,
    page_footer: bool = True,
    page_header: bool = True,
    picture: bool = True,
    section_header: bool = True,
    table: bool = True,
    text: bool = True,
    title: bool = True,
):
    """Extract text from PDF by segment types"""
    try:
        if pdf_file is None:
            return "Error: No PDF file provided", ""

        # Build the types string from checkboxes
        selected_types = []
        if caption:
            selected_types.append("Caption")
        if footnote:
            selected_types.append("Footnote")
        if formula:
            selected_types.append("Formula")
        if list_item:
            selected_types.append("List item")
        if page_footer:
            selected_types.append("Page footer")
        if page_header:
            selected_types.append("Page header")
        if picture:
            selected_types.append("Picture")
        if section_header:
            selected_types.append("Section header")
        if table:
            selected_types.append("Table")
        if text:
            selected_types.append("Text")
        if title:
            selected_types.append("Title")

        # If no types selected, use "all"
        types = ",".join(selected_types) if selected_types else "all"

        with open(pdf_file, "rb") as f:
            files = {"file": f}
            data = {"fast": str(fast_mode).lower(), "types": types}
            response = call_api("/text", files=files, data=data)

        # The /text endpoint returns plain text, not JSON
        text_content = response.text

        # Format results
        summary = "✓ Text extraction complete!\n\n"
        summary += f"Extracted {len(text_content)} characters"

        return summary, text_content
    except Exception as e:
        return f"Error: {str(e)}", ""


def select_all_types():
    """Select all segment types"""
    return [True] * 11  # Return True for all 11 checkboxes


def deselect_all_types():
    """Deselect all segment types"""
    return [False] * 11  # Return False for all 11 checkboxes


def extract_toc(pdf_file: str, fast_mode: bool = False):
    """Extract table of contents from PDF"""
    try:
        if pdf_file is None:
            return "Error: No PDF file provided", ""

        with open(pdf_file, "rb") as f:
            files = {"file": f}
            data = {"fast": str(fast_mode).lower()}
            response = call_api("/toc", files=files, data=data)

        result = response.json()

        # Format results
        # The /toc endpoint returns a list of dicts with 'label', 'indentation', and 'bounding_box' (which contains 'page')
        if isinstance(result, list) and len(result) > 0:
            summary = "✓ Found {} TOC entries\n\n".format(len(result))
            toc_text = ""
            for item in result:
                if isinstance(item, dict):
                    label = item.get("label", "Unknown")
                    indentation = item.get("indentation", 0)
                    bounding_box = item.get("bounding_box", {})
                    page = bounding_box.get("page", "?")
                    indent = "  " * indentation
                    toc_text += f"{indent}- {label} (page {page})\n"
                else:
                    toc_text += f"{item}\n"
        else:
            summary = "No table of contents found or unable to extract TOC"
            toc_text = json.dumps(result, indent=2)

        return summary, toc_text
    except Exception as e:
        return f"Error: {str(e)}", ""


def visualize_pdf(pdf_file: str, fast_mode: bool = False):
    """Create visualization of PDF with detected segments"""
    try:
        if pdf_file is None:
            return "Error: No PDF file provided", "", None

        with open(pdf_file, "rb") as f:
            files = {"file": f}
            data = {"fast": str(fast_mode).lower()}
            response = call_api("/visualize", files=files, data=data)

        # Save the PDF response to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            output_path = tmp_file.name

        # Create an HTML iframe to display the PDF
        # Encode PDF as base64 for embedding
        pdf_base64 = base64.b64encode(response.content).decode("utf-8")
        pdf_display_html = f"""
        <iframe 
            src="data:application/pdf;base64,{pdf_base64}" 
            width="100%" 
            height="800px" 
            style="border: 1px solid #ccc; border-radius: 4px;">
            <p>Your browser does not support PDFs. 
            <a href="data:application/pdf;base64,{pdf_base64}" download="visualization.pdf">Download the PDF</a> instead.</p>
        </iframe>
        """

        return "✓ Visualization created successfully!", pdf_display_html, output_path
    except Exception as e:
        return f"Error: {str(e)}", "", None


def process_ocr(pdf_file: str, language: str = "en"):
    """Process PDF with OCR"""
    try:
        if pdf_file is None:
            return "Error: No PDF file provided", None

        with open(pdf_file, "rb") as f:
            files = {"file": f}
            data = {"language": language}
            response = call_api("/ocr", files=files, data=data)

        # Save the PDF response to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            output_path = tmp_file.name

        return f"✓ OCR processing complete! Language: {language}", output_path
    except Exception as e:
        return f"Error: {str(e)}", None


def convert_to_markdown(
    pdf_file: str,
    fast_mode: bool = False,
    extract_toc: bool = False,
    dpi: int = 120,
    target_languages: str = "",
    translation_model: str = "gpt-oss",
):
    """Convert PDF to Markdown format"""
    try:
        if pdf_file is None:
            return "Error: No PDF file provided", None

        # Get the original filename without extension
        original_filename = os.path.splitext(os.path.basename(pdf_file))[0]
        output_filename = f"{original_filename}.md"

        with open(pdf_file, "rb") as f:
            files = {"file": f}
            data = {
                "fast": str(fast_mode).lower(),
                "extract_toc": str(extract_toc).lower(),
                "dpi": str(dpi),
                "target_languages": target_languages if target_languages else "",
                "translation_model": translation_model,
                # Include output_file to get zip with images and segmentation
                "output_file": output_filename,
            }
            response = call_api("/markdown", files=files, data=data)

        # When output_file is provided, the API always returns a ZIP file
        # Save the ZIP file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
            tmp_file.write(response.content)
            output_path = tmp_file.name

        summary = "✓ Converted to Markdown successfully!\n"
        summary += "Download the ZIP file below (contains markdown, images, and segmentation data)"
        if target_languages and target_languages.strip():
            summary += f"\nIncludes translations to: {target_languages}"

        return summary, output_path
    except Exception as e:
        return f"Error: {str(e)}", None


def convert_to_html(
    pdf_file: str,
    fast_mode: bool = False,
    extract_toc: bool = False,
    dpi: int = 120,
    target_languages: str = "",
    translation_model: str = "gpt-oss",
):
    """Convert PDF to HTML format"""
    try:
        if pdf_file is None:
            return "Error: No PDF file provided", None

        # Get the original filename without extension
        original_filename = os.path.splitext(os.path.basename(pdf_file))[0]
        output_filename = f"{original_filename}.html"

        with open(pdf_file, "rb") as f:
            files = {"file": f}
            data = {
                "fast": str(fast_mode).lower(),
                "extract_toc": str(extract_toc).lower(),
                "dpi": str(dpi),
                "target_languages": target_languages if target_languages else "",
                "translation_model": translation_model,
                # Include output_file to get zip with images and segmentation
                "output_file": output_filename,
            }
            response = call_api("/html", files=files, data=data)

        # When output_file is provided, the API always returns a ZIP file
        # Save the ZIP file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
            tmp_file.write(response.content)
            output_path = tmp_file.name

        summary = "✓ Converted to HTML successfully!\n"
        summary += "Download the ZIP file below (contains HTML, images, and segmentation data)"
        if target_languages and target_languages.strip():
            summary += f"\nIncludes translations to: {target_languages}"

        return summary, output_path
    except Exception as e:
        return f"Error: {str(e)}", None


# Create the Gradio interface
with gr.Blocks(
    title="PDF Document Layout Analysis",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1400px !important;
    }
    .output-text {
        font-family: 'Monaco', 'Courier New', monospace;
    }
    """,
) as app:
    gr.Markdown(
        f"""
        # 📄 PDF Document Layout Analysis Tool
        
        A comprehensive tool for analyzing PDF documents using deep learning models.
        Upload a PDF and use the tabs below to perform various analyses.
        
        **Connected to API:** `{API_BASE_URL}`
        """
    )

    # System Info Section
    with gr.Accordion("ℹ️ System Information", open=False):
        gr.Markdown("Click the button below to view system and configuration information.")
        info_btn = gr.Button("Get System Info", variant="secondary")
        info_output = gr.Textbox(label="System Information", lines=10, elem_classes="output-text")
        info_btn.click(fn=get_system_info, outputs=info_output)

    gr.Markdown("---")

    # Main tabs for different functionalities
    with gr.Tabs():
        # Tab 1: Visualization
        with gr.Tab("🎨 Visualization"):
            gr.Markdown("Visualize the detected layout segments on your PDF pages.")
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_viz = gr.File(label="Upload PDF", file_types=[".pdf"])
                    fast_mode_viz = gr.Checkbox(label="Fast Mode", value=False)
                    viz_btn = gr.Button("Create Visualization", variant="primary")

                with gr.Column(scale=2):
                    viz_summary = gr.Textbox(label="Summary", lines=2)
                    viz_display = gr.HTML(label="Visualized PDF Preview")
                    viz_output = gr.File(label="Download Visualization PDF")

            viz_btn.click(
                fn=visualize_pdf, inputs=[pdf_input_viz, fast_mode_viz], outputs=[viz_summary, viz_display, viz_output]
            )

        # Tab 2: PDF Analysis
        with gr.Tab("📊 PDF Analysis"):
            gr.Markdown("Analyze the layout and structure of your PDF document.")
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_analyze = gr.File(label="Upload PDF", file_types=[".pdf"])
                    fast_mode_analyze = gr.Checkbox(label="Fast Mode", value=False)
                    parse_tables = gr.Checkbox(label="Parse Tables and Math", value=False)
                    analyze_btn = gr.Button("Analyze PDF", variant="primary")

                with gr.Column(scale=2):
                    analyze_summary = gr.Textbox(label="Summary", lines=8)
                    analyze_details = gr.Textbox(
                        label="Detailed Results (JSON)", lines=15, elem_classes="output-text", show_copy_button=True
                    )

            analyze_btn.click(
                fn=analyze_pdf,
                inputs=[pdf_input_analyze, fast_mode_analyze, parse_tables],
                outputs=[analyze_summary, analyze_details],
            )

        # Tab 3: Text Extraction
        with gr.Tab("📝 Text Extraction"):
            gr.Markdown("Extract text content from your PDF, optionally filtered by segment types.")
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_text = gr.File(label="Upload PDF", file_types=[".pdf"])
                    fast_mode_text = gr.Checkbox(label="Fast Mode", value=False)

                    gr.Markdown("**Segment Types:**")
                    with gr.Row():
                        select_all_btn = gr.Button("Select All", size="sm")
                        deselect_all_btn = gr.Button("Deselect All", size="sm")

                    caption_check = gr.Checkbox(label="Caption", value=True)
                    footnote_check = gr.Checkbox(label="Footnote", value=True)
                    formula_check = gr.Checkbox(label="Formula", value=True)
                    list_item_check = gr.Checkbox(label="List item", value=True)
                    page_footer_check = gr.Checkbox(label="Page footer", value=True)
                    page_header_check = gr.Checkbox(label="Page header", value=True)
                    picture_check = gr.Checkbox(label="Picture", value=True)
                    section_header_check = gr.Checkbox(label="Section header", value=True)
                    table_check = gr.Checkbox(label="Table", value=True)
                    text_check = gr.Checkbox(label="Text", value=True)
                    title_check = gr.Checkbox(label="Title", value=True)

                    extract_text_btn = gr.Button("Extract Text", variant="primary")

                with gr.Column(scale=2):
                    text_summary = gr.Textbox(label="Summary", lines=3)
                    text_output = gr.Textbox(
                        label="Extracted Text", lines=20, elem_classes="output-text", show_copy_button=True
                    )

            # Store all checkboxes in a list for easier management
            type_checkboxes = [
                caption_check,
                footnote_check,
                formula_check,
                list_item_check,
                page_footer_check,
                page_header_check,
                picture_check,
                section_header_check,
                table_check,
                text_check,
                title_check,
            ]

            # Select all and deselect all button functionality
            select_all_btn.click(fn=select_all_types, outputs=type_checkboxes)
            deselect_all_btn.click(fn=deselect_all_types, outputs=type_checkboxes)

            extract_text_btn.click(
                fn=extract_text,
                inputs=[pdf_input_text, fast_mode_text] + type_checkboxes,
                outputs=[text_summary, text_output],
            )

        # Tab 4: Table of Contents
        with gr.Tab("📑 Table of Contents"):
            gr.Markdown("Extract the table of contents structure from your PDF.")
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_toc = gr.File(label="Upload PDF", file_types=[".pdf"])
                    fast_mode_toc = gr.Checkbox(label="Fast Mode", value=False)
                    toc_btn = gr.Button("Extract TOC", variant="primary")

                with gr.Column(scale=2):
                    toc_summary = gr.Textbox(label="Summary", lines=3)
                    toc_output = gr.Textbox(
                        label="Table of Contents", lines=20, elem_classes="output-text", show_copy_button=True
                    )

            toc_btn.click(fn=extract_toc, inputs=[pdf_input_toc, fast_mode_toc], outputs=[toc_summary, toc_output])

        # Tab 5: OCR Processing
        with gr.Tab("🔍 OCR Processing"):
            gr.Markdown("Apply OCR (Optical Character Recognition) to extract text from scanned PDFs.")
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_ocr = gr.File(label="Upload PDF", file_types=[".pdf"])
                    language_input = gr.Dropdown(
                        label="OCR Language",
                        choices=[
                            "en",
                            "fra",
                            "spa",
                            "deu",
                            "ara",
                            "mya",
                            "hin",
                            "tam",
                            "tha",
                            "chi_sim",
                            "tur",
                            "ukr",
                            "ell",
                            "rus",
                            "kor",
                        ],
                        value="en",
                    )
                    ocr_btn = gr.Button("Process OCR", variant="primary")

                with gr.Column(scale=2):
                    ocr_summary = gr.Textbox(label="Summary", lines=2)
                    ocr_output = gr.File(label="Download OCR-processed PDF")

            ocr_btn.click(fn=process_ocr, inputs=[pdf_input_ocr, language_input], outputs=[ocr_summary, ocr_output])

        # Tab 6: Markdown Conversion
        with gr.Tab("📄 Markdown Conversion"):
            gr.Markdown(
                """Convert your PDF to Markdown format with optional translation. Returns a ZIP file with markdown, images, and segmentation data.
                _For translation support, you should start the service with `just start_gui_translation` command._
                """
            )
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_md = gr.File(label="Upload PDF", file_types=[".pdf"])
                    fast_mode_md = gr.Checkbox(label="Fast Mode", value=False)
                    extract_toc_md = gr.Checkbox(label="Add TOC", value=False)
                    dpi_md = gr.Slider(label="DPI", minimum=72, maximum=300, value=120, step=1)
                    target_langs_md = gr.Textbox(
                        label="Target Languages (comma-separated)",
                        placeholder='e.g., "Turkish", "Spanish", "French" (leave empty for no translation)',
                    )
                    translation_model_md = gr.Dropdown(label="Translation Model", choices=["gpt-oss"], value="gpt-oss")
                    md_btn = gr.Button("Convert to Markdown", variant="primary")

                with gr.Column(scale=2):
                    md_summary = gr.Textbox(label="Summary", lines=2)
                    md_output = gr.File(label="Download ZIP (contains Markdown + images + segmentation)")

            md_btn.click(
                fn=convert_to_markdown,
                inputs=[pdf_input_md, fast_mode_md, extract_toc_md, dpi_md, target_langs_md, translation_model_md],
                outputs=[md_summary, md_output],
            )

        # Tab 7: HTML Conversion
        with gr.Tab("🌐 HTML Conversion"):
            gr.Markdown(
                """Convert your PDF to HTML format with optional translation. Returns a ZIP file with HTML, images, and segmentation data.
                _For translation support, you should start the service with `just start_gui_translation` command._
                """
            )
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input_html = gr.File(label="Upload PDF", file_types=[".pdf"])
                    fast_mode_html = gr.Checkbox(label="Fast Mode", value=False)
                    extract_toc_html = gr.Checkbox(label="Add TOC", value=False)
                    dpi_html = gr.Slider(label="DPI", minimum=72, maximum=300, value=120, step=1)
                    target_langs_html = gr.Textbox(
                        label="Target Languages (comma-separated)",
                        placeholder='e.g., "Turkish", "Spanish", "French" (leave empty for no translation)',
                    )
                    translation_model_html = gr.Dropdown(label="Translation Model", choices=["gpt-oss"], value="gpt-oss")
                    html_btn = gr.Button("Convert to HTML", variant="primary")

                with gr.Column(scale=2):
                    html_summary = gr.Textbox(label="Summary", lines=2)
                    html_output = gr.File(label="Download ZIP (contains HTML + images + segmentation)")

            html_btn.click(
                fn=convert_to_html,
                inputs=[
                    pdf_input_html,
                    fast_mode_html,
                    extract_toc_html,
                    dpi_html,
                    target_langs_html,
                    translation_model_html,
                ],
                outputs=[html_summary, html_output],
            )

    gr.Markdown(
        """
        ---
        ### 💡 Tips
        - **Fast Mode**: Uses a lighter model for faster processing with slightly reduced accuracy
        - **Parse Tables and Math**: Enables specialized extraction for tables and mathematical formulas
        - **DPI**: 
            - For OCR processing, the value specifies the DPI of the input PDF which is used for OCR.
            - For conversion to Markdown and HTML, the value specifies the DPI of the extracted images.
        """
    )


if __name__ == "__main__":
    print("Starting Gradio interface...")
    print(f"API Base URL: {API_BASE_URL}")

    # Store the original get_api_info method
    import gradio
    from gradio_client import utils as client_utils

    original_get_api_info = gradio.Blocks.get_api_info

    # Monkey-patch the problematic json_schema_to_python_type function
    # to handle the bool schema bug in Gradio 4.40.0
    original_json_schema_to_python_type = client_utils.json_schema_to_python_type

    def patched_json_schema_to_python_type(schema):
        """Patched version that handles bool schemas"""
        try:
            # If schema is a bool (which causes the bug), convert it to a simple dict
            if isinstance(schema, bool):
                return "any"
            return original_json_schema_to_python_type(schema)
        except TypeError as e:
            if "argument of type 'bool' is not iterable" in str(e):
                return "any"
            raise

    # Apply the patch
    client_utils.json_schema_to_python_type = patched_json_schema_to_python_type

    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
