FROM centos:centos8.2.2004

RUN dnf module install -y python39 python39-devel
RUN dnf module install -y wget gcc jq
RUN pip3 install --upgrade pip
RUN pip3 install qas==1.0.6
RUN alias ls='ls --color'
