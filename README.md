<h3 align="center">PDF Document Layout Analysis</h3>
<p align="center">A Docker-powered service for PDF document layout analysis</p>

---
This project provides a powerful and flexible PDF analysis service. The service allows for 
the segmentation and classification of different parts of PDF pages, identifying the elements such as texts, titles, 
pictures, tables and so on. Additionally, it determines the correct order of these identified elements.


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


## Quick Start
Start the service:

    # With GPU support
    make start
    
    # Without GPU support [if you do not have a GPU on your system]
    make start_no_gpu

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
- [Benchmark](#benchmark)

## Dependencies
* Docker Desktop 4.25.0 [install link](https://www.docker.com/products/docker-desktop/)
* For GPU support [install link](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Requirements
* 4 GB RAM memory
* 6 GB GPU memory (if not, it will run with CPU)
  
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

## Data

As we mentioned, we are using the visual model that trained on [DocLayNet](https://github.com/DS4SD/DocLayNet) dataset. 
Also for training the LightGBM models, we again used this dataset. There are 11 categories in this dataset:

       1: "Caption"
       2: "Footnote"
       3: "Formula"
       4: "ListItem"
       5: "PageFooter"
       6: "PageHeader"
       7: "Picture"
       8: "SectionHeader"
       9: "Table"
       10: "Text"
       11: "Title"

For more information about the data, you can visit the link we shared above.

## Usage

As we mentioned at the [Quick Start](#quick-start), you can use the service simply like this:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060

This command will run the code on visual model. So you should be prepared that it will use lots of resources. But if you
want to use the not visual models, which are the LightGBM models, you can use this command:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060/fast

The shape of the response will be the same in both of these commands. 


When the process is done, the output will include a list of SegmentBox elements and, every SegmentBox element will has this information:

        {
            "left": Left position of the segment
            "top": Top position of the segment
            "width": Width of the segment
            "height": Height of the segment
            "page_number": Page number which the segment belongs to
            "text": Text inside the segment
            "type": Type of the segment (one of the categories mentioned above)
        }

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


## Benchmark

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