FROM centos:7

MAINTAINER Tiago Teixeira <tteixeira@ubiwhere.com>

RUN yum -y update && \
yum --enablerepo=extras install -y epel-release && \
yum -y groupinstall development && \
yum install -y wget git && \
yum clean all

# Install Python3 and PIP
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm && \
yum -y install python36u && \
yum -y install python36u-pip && \
yum install -y python-pip && \
pip3.6 install --upgrade pip

RUN yum -y install python36u-devel

ENV PATH =/usr/local/bin:${PATH}

# Create necessary Folders
RUN mkdir /app/

# Add all required files
COPY requirements.txt /app/

# Install server requirementser
WORKDIR /app/

RUN pip3.6 install -r requirements.txt

# ADD the remaining files
COPY wsgi.ini /app/
COPY service /app/service
COPY service.pth /lib/python3.6/site-packages/

# Create all ENV
ENV GUNICORN_BIND=0.0.0.0:7000

# Run bootstrap
CMD ["paster", "serve", "wsgi.ini"]
