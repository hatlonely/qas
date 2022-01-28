FROM centos:centos8

RUN dnf module -y install python39 && pip3 install --upgrade pip
RUN dnf install -y wget unzip gcc python39-devel jq crontabs git make
RUN pip3 uninstall pycrypto && pip3 install pycrypto
RUN alias ls='ls --color'

COPY qas qas/qas
COPY setup.py qas/setup.py
COPY bin qas/bin
COPY requirements.txt qas/requirements.txt
COPY README.md qas/README.md
COPY LICENSE qas/LICENSE

RUN cd qas && \
    python3 setup.py install && \
    pip3 install -r requirements.txt && \
    cd - && rm -rf qas
