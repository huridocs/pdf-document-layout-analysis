<h3 align="center">PDF document layout analysis</h3>
<p align="center">A Docker-powered service for PDF document layout analysis</p>

---
[ Descriptions needed ]


## Quick Start
Start the service:

    # With GPU support
    make start
    
    # Without GPU support
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

## Dependencies
* Docker Desktop 4.25.0 [install link](https://www.docker.com/products/docker-desktop/)
* For GPU support [install link](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Requirements
* 4 GB RAM memory
* 7 GB GPU memory (if not, it will run with CPU)
  
## Models

There are two kinds of models in the project. The default model is a visual model which has been trained by
Alibaba Research Group. If you would like to take a look at their original project, you can visit
[this](https://github.com/AlibabaResearch/AdvancedLiterateMachinery) link. There are various models published by them
and according to our benchmarks the best performing model is the one trained with the [DocLayNet](https://github.com/DS4SD/DocLayNet)
dataset. So, this model is the default model in our project, and it uses more resources than the other model which we ourselves trained.

The second kind of model is the LightGBM models. These models are not visual models, they do not "see" the pages, but
we are using XML information that we extracted by using Poppler. The reason there are two models existed is, one of these
models is predicting the types of the tokens and the other one is trying to find out the correct segmentations in the page.
By combining both, we are segmenting the pages alongside with the type of the content.

Even though the visual model using more resources than the others, generally it's giving better performance since it 
"sees" the whole page and has an idea about all the context. On the other hand, LightGBM models are not performing that well
but they are much faster and more resource-friendly. It will only require your CPU power.

## Data

As we mentioned, we are using the visual model that trained on [DocLayNet](https://github.com/DS4SD/DocLayNet) dataset. 
Also for training the LightGBM models, we again used this dataset. There are 11 categories:

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

As we mentioned at the [Quick Start](#quick-start), you can start the service simply like this:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060

This command will run the code on visual model. So you should be prepared that it will use lots of resources. But if you
want to use the not visual models, which are the LightGBM models, you can use this command:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060/fast

The shape of the response will be the same in both of these commands. 


When the process is done, the output includes list of SegmentBox elements and, every SegmentBox element has this information:

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