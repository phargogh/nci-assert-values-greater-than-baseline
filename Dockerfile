FROM --platform=linux/amd64 conda/miniconda3

RUN conda install -y -c conda-forge pygeoprocessing taskgraph

ENTRYPOINT ["/usr/local/bin/python"]
