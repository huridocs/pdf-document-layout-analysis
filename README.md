
<h3 align="center">PDF Document Layout Analysis</h3>
<p align="center">A Docker-powered service for PDF document layout analysis and PDF OCR</p>

---
This project provides a powerful and flexible PDF analysis service. The service enables OCR, 
segmentation, and classification of different parts of PDF pages, 
identifying elements such as texts, titles, pictures, tables, and so on. 
Additionally, it determines the correct order of these identified elements.


<table>
  <tr>
    <td>
      <img src="https://raw.githubusercontent.com/huridocs/pdf-document-layout-analysis/main/images/vgtexample1.png"/>
    </td>
    <td>
      <img src="https://raw.githubusercontent.com/huridocs/pdf-document-layout-analysis/main/images/vgtexample2.png"/>
    </td>
    <td>
      <img src="https://raw.githubusercontent.com/huridocs/pdf-document-layout-analysis/main/images/vgtexample3.png"/>
    </td>
    <td>
      <img src="https://raw.githubusercontent.com/huridocs/pdf-document-layout-analysis/main/images/vgtexample4.png"/>
    </td>
  </tr>
</table>

#### Project Links:

- GitHub: [pdf-document-layout-analysis](https://github.com/huridocs/pdf-document-layout-analysis)
- HuggingFace: [pdf-document-layout-analysis](https://huggingface.co/HURIDOCS/pdf-document-layout-analysis)
- DockerHub: [pdf-document-layout-analysis](https://hub.docker.com/r/huridocs/pdf-document-layout-analysis/)

---

## Quick Start
Run the service:

- With GPU support:
  
      make start


- Without GPU support:

      make start_no_gpu


[OPTIONAL] OCR the PDF. Check supported languages (curl localhost:5060/info) or [install more languages for OCR](#installation-of-more-languages-for-ocr):

    curl -X POST -F 'language=en' -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060/ocr --output ocr_document.pdf


Get the segments from a PDF:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060

To stop the server:

    make stop


## Contents
- [Quick Start](#quick-start)
- [Dependencies](#dependencies)
- [Requirements](#requirements)
- [Models](#models)
- [Data](#data)
- [Usage](#usage)
- [Benchmarks](#benchmarks)
  - [Performance](#performance)
  - [Speed](#speed)
- [Installation of More Languages for OCR](#installation-of-more-languages-for-ocr)
- [Related Services](#related-services)

## Dependencies
* Docker Desktop 4.25.0 [install link](https://www.docker.com/products/docker-desktop/)
* For GPU support [install link](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Requirements
* 2 GB RAM memory
* 5 GB GPU memory (if not, it will run on CPU)
  
## Models

There are two kinds of models in the project. The default model is a visual model (specifically called as Vision Grid Transformer - VGT)
which has been trained by Alibaba Research Group. If you would like to take a look at their original project, you can visit
[this](https://github.com/AlibabaResearch/AdvancedLiterateMachinery) link. There are various models published by them
and according to our benchmarks the best performing model is the one trained with the [DocLayNet](https://github.com/DS4SD/DocLayNet)
dataset. So, this model is the default model in our project, and it uses more resources than the other model which we ourselves trained.

The second kind of model is the LightGBM models. These models are not visual models, they do not "see" the pages, but
we are using XML information that we extracted by using [Poppler](https://poppler.freedesktop.org). The reason there are two 
models existed is, one of these models is predicting the types of the tokens and the other one is trying to find out the correct segmentations in the page.
By combining both, we are segmenting the pages alongside with the type of the content.

Even though the visual model using more resources than the others, generally it's giving better performance since it 
"sees" the whole page and has an idea about all the context. On the other hand, LightGBM models are performing slightly worse
but they are much faster and more resource-friendly. It will only require your CPU power.

The service converts PDFs to text-searchable PDFs using [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [ocrmypdf](https://ocrmypdf.readthedocs.io/en/latest/index.html).

## Data

As we mentioned, we are using the visual model that trained on [DocLayNet](https://github.com/DS4SD/DocLayNet) dataset. 
Also for training the LightGBM models, we again used this dataset. There are 11 categories in this dataset:

       1: "Caption"
       2: "Footnote"
       3: "Formula"
       4: "List item"
       5: "Page footer"
       6: "Page header"
       7: "Picture"
       8: "Section header"
       9: "Table"
       10: "Text"
       11: "Title"

For more information about the data, you can visit the link we shared above.

## Usage

As we mentioned at the [Quick Start](#quick-start), you can use the service simply like this:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060

This command will run the visual model. So you should be prepared that it will use lots of resources. Also, please note 
that if you do not have GPU in your system, or if you do not have enough free GPU memory, the visual model will run on CPU. 
You should be expecting a long response time in that case (See [speed benchmark](#speed) for more details).


If you want to use the non-visual models, which are the LightGBM models, you can use this command:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' -F "fast=true" localhost:5060

The shape of the response will be the same in both of these commands. 


When the process is done, the output will include a list of SegmentBox elements and, every SegmentBox element will has this information:

        {
            "left": Left position of the segment
            "top": Top position of the segment
            "width": Width of the segment
            "height": Height of the segment
            "page_number": Page number which the segment belongs to
            "page_width": Width of the page which the segment belongs to 
            "page_height": Width of the page which the segment belongs to
            "text": Text inside the segment
            "type": Type of the segment (one of the categories mentioned above)
        }


If you want to get the visualizations, you can use this command:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060/visualize -o '/PATH/TO/OUTPUT_PDF/pdf_name.pdf'

Or with fast models:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' -F "fast=true" localhost:5060/visualize -o '/PATH/TO/OUTPUT_PDF/pdf_name.pdf'



And to stop the server, you can simply use this:

    make stop

### Order of the Output Elements

When all the processes are done, the service returns a list of SegmentBox elements with some determined order. To figure out this order,
we are mostly relying on [Poppler](https://poppler.freedesktop.org). In addition to this, we are also getting help from the types of the segments.

During the PDF to XML conversion, Poppler determines an initial reading order for each token it creates. These tokens are typically lines of text,
but it depends on Poppler's heuristics. When we extract a segment, it usually consists of multiple tokens. Therefore, for each segment on the page,
we calculate an "average reading order" by averaging the reading orders of the tokens within that segment. We then sort the segments 
based on this average reading order. However, this process is not solely dependent on Poppler, we also consider the types of segments.

First, we place the "header" segments at the beginning and sort them among themselves. Next, we sort the remaining segments, 
excluding "footers" and "footnotes," which are positioned at the end of the output.

Occasionally, we encounter segments like pictures that might not contain text. Since Poppler cannot assign a reading order to these non-text segments, 
we process them after sorting all segments with content. To determine their reading order, we rely on the reading order of the nearest "non-empty" segment, 
using distance as a criterion.


### Extracting Tables and Formulas

Our service provides a way to extract your tables and formulas in different formats. 

As default, formula segments' "text" property will include the formula in LaTeX format.

You can also extract tables in different formats like "markdown", "latex", or "html" but this is not a default option.  
To extract the tables like this, you should set "extraction_format" parameter. Some example usages shown below:

```
curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060 -F "extraction_format=latex"
```
```
curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060/fast -F "extraction_format=markdown"
```

You should be aware that this additional extraction process can make the process much longer, especially if you have a large number of tables.

(For table extraction, we are using [StructEqTable](https://github.com/UniModal4Reasoning/StructEqTable-Deploy) 
and for formula extraction, we are using [RapidLaTeXOCR](https://github.com/RapidAI/RapidLaTeXOCR))


## Benchmarks

### Performance

These are the benchmark results for VGT model on PubLayNet dataset:

<table>
  <tr>
    <th>Overall</th>
    <th>Text</th>
    <th>Title</th>
    <th>List</th>
    <th>Table</th>
    <th>Figure</th>
  </tr>
  <tr>
    <td>0.962</td>
    <td>0.950</td>
    <td>0.939</td>
    <td>0.968</td>
    <td>0.981</td>
    <td>0.971</td>
  </tr>
</table>

You can check this link to see the comparison with the other models: https://paperswithcode.com/sota/document-layout-analysis-on-publaynet-val

### Speed

For 15 pages academic paper document:

<table>
  <tr>
    <th>Model</th>
    <th>GPU</th>
    <th>Speed (seconds per page)</th>
  </tr>
  <tr>
    <td>Fast Model</td>
    <td>✗ [i7-8700 3.2GHz]</td>
    <td>0.42</td>
  </tr>
  <tr>
    <td>VGT</td>
    <td>✓ [GTX 1070]</td>
    <td>1.75</td>
  </tr>
  <tr>
    <td>VGT</td>
    <td>✗ [i7-8700 3.2GHz]</td>
    <td>13.5</td>
  </tr>
</table>


## Installation of More Languages for OCR

OCR is made by using Tesseract OCR, which is supporting +150 languages, however, the docker image is built with only a few languages (image size purposes). 

More languages can be used by installing them in the docker container or installing them in your local machine (if you are running the service locally).

To install more languages in the docker container, you can use the following command after the container is running:

    docker exec -it --user root pdf-document-layout-analysis /bin/bash
    apt-get install tesseract-ocr-[LANGCODES]

Tesseract `LANGCODES` can be found in here: [iso_to_tesseract dict](https://github.com/huridocs/pdf-document-layout-analysis/blob/main/src/ocr/languages.py).

For example, to install "Korean" support, you can run:

```
docker exec -it --user root pdf-document-layout-analysis /bin/bash
apt-get install tesseract-ocr-kor
```

After installing the languages you can confirm it by running:

```
curl localhost:5060/info
```


## Related Services
Here are some of our other services that is built upon this service:

- [PDF Table Of Contents Extractor](https://github.com/huridocs/pdf-table-of-contents-extractor): This project aims to extract text from PDF files using the outputs generated 
by the pdf-document-layout-analysis service. By leveraging  the segmentation and classification capabilities of the underlying analysis tool, 
this project automates the process of text extraction from PDF files.


- [PDF Text Extraction](https://github.com/huridocs/pdf-text-extraction): This project aims to extract text from PDF files using the outputs generated by the 
pdf-document-layout-analysis service. By leveraging the segmentation and classification capabilities of the underlying
analysis tool, this project automates the process of text extraction from PDF files.


