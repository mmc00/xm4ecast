# This is miniconda ubuntu docker image

## arguments
ARG UBUNTU_VER=22.04
ARG CONDA_VER=latest
ARG PY_VER=3.9
ARG OS_TYPE=x86_64

## script
FROM ubuntu:${UBUNTU_VER}

### system packages
RUN apt-get update && apt-get install -yq curl wget jq vim

### arguments during the building
ARG CONDA_VER
ARG OS_TYPE

### install miniconda to /miniconda
RUN curl -LO "http://repo.continuum.io/miniconda/Miniconda3-${CONDA_VER}-Linux-${OS_TYPE}.sh"
RUN bash Miniconda3-${CONDA_VER}-Linux-${OS_TYPE}.sh -p /miniconda -b
RUN rm Miniconda3-${CONDA_VER}-Linux-${OS_TYPE}.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

### arguments during the building
ARG PY_VER
### install packages from conda and downgrade py (optional).
RUN conda install -c anaconda -y python=${PY_VER}
RUN pip install numpy=1.20.3 && pip install pandas=1.3.4 && pip install requests==2.26.0

### copy the files
COPY src/data/cbk_data.py ./
COPY src/data/main_cbk.py ./

### running the files
CMD ["python",  "./main_cbk.py"]