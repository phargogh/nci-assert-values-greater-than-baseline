FROM --platform=linux/amd64 conda/miniconda3

RUN conda install -y pygeoprocessing taskgraph

ENTRYPOINT ["/usr/bin/python"]


