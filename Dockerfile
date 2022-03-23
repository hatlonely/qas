FROM centos:centos8

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Linux-*
RUN dnf install -y python39 python39-devel wget gcc jq
RUN pip3 install --upgrade pip && pip3 install wheel
RUN wget https://download-ib01.fedoraproject.org/pub/epel/8/Everything/x86_64/Packages/t/thrift-0.13.0-2.el8.x86_64.rpm
RUN rpm -ivh thrift-0.13.0-2.el8.x86_64.rpm && rm thrift-0.13.0-2.el8.x86_64.rpm
RUN pip3 install qas==1.0.7
