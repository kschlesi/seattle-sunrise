from python:3.7 as build_layer

COPY . /tmp
RUN cd /tmp && pip install .

from python:3.7

COPY --from=build_layer /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
