FROM centos:centos8

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Linux-*
RUN dnf install -y python39
RUN dnf install -y python39-devel wget gcc jq
RUN pip3 install --upgrade pip
RUN pip3 install wheel
RUN pip3 install qas==1.0.6
RUN alias ls='ls --color'
