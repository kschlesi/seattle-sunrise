from python:3.7 as build_layer

COPY . /usr/local/src/
RUN cd /usr/local/src && pip install -e .

from python:3.7

COPY --from=build_layer /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY --from=build_layer /usr/local/bin /usr/local/bin
COPY --from=build_layer /usr/local/src /usr/local/src
