<h3 align="center">PDF document layout analysis</h3>
<p align="center">A Docker-powered service for PDF document layout analysis</p>

---
[ Descriptions needed ]


## Quick Start
Start the service:

    # Without GPU support
    make start_no_gpu

    # With GPU support
    make start

Get the segments from a PDF:

    curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5060

To stop the server:

    make stop

## Contents
- [Quick Start](#quick-start)
- [Dependencies](#dependencies)
- [Requirements](#requirements)


## Dependencies
* Docker Desktop 4.25.0 [install link](https://www.docker.com/products/docker-desktop/)
* For GPU support [install link](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## Requirements
* 2Gb RAM memory
* Single core
  
