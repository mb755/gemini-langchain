FROM continuumio/miniconda3

RUN mkdir -p gemini-langchain

COPY . /gemini-langchain
WORKDIR /gemini-langchain

RUN apt-get update && apt-get install -y doxygen graphviz git

RUN conda env create --name gemini-langchain --file environment.yml

RUN echo "conda activate gemini-langchain" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

RUN pre-commit install
