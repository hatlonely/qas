FROM centos:centos8

RUN dnf module -y install python39 && pip3 install --upgrade pip
COPY . qas

RUN cd qas && \
    python3 setup.py install && \
    pip3 install -r requirements.txt &&
    cd - && rm -rf qas
