FROM ubuntu

RUN apt-get update && apt-get install -y git python3-pip python3-dev build-essential libevent-pthreads-2.1-6 swig3.0

RUN git clone https://github.com/epfml/sent2vec.git

RUN mkdir -p /opt/sent2vec/src
RUN cp sent2vec/setup.py /opt/sent2vec/
RUN cp -r sent2vec/src /opt/sent2vec/
RUN cp sent2vec/Makefile /opt/sent2vec/
RUN cp sent2vec/requirements.txt /opt/sent2vec/

RUN apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen

WORKDIR /opt/sent2vec

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN pip3 install .
RUN make

WORKDIR /app

ADD ./helpers /app/helpers
ADD ./smafed /app/smafed
COPY ./delete_cluster.py /app
COPY ./event_detection.py /app
COPY ./requirements.txt /app
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "./event_detection.py"]
