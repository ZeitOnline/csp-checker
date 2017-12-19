FROM markadams/chromium-xvfb-py3

RUN apt-get update && apt-get install -y \
    libxml2-dev libxslt-dev python-dev zlib1g-dev

ADD crawler_requirements.txt /
ADD crawler.py /
RUN pip3 install -r /crawler_requirements.txt
CMD [ "python3", "/crawler.py"]

