FROM --platform=linux/amd64 conda/miniconda3:2141bfc4b60cc5eb332402207c80d884daa72fcefa48b50f3ccadd934d1f3d03

RUN: conda install -y pygeoprocessing taskgraph

ENTRYPOINT: ["/usr/bin/python"]


