FROM dkarchmervue/moviepy:latest
#RUN apt-get update
#RUN apt-get install -y
RUN pip install Pillow python-resize-image
RUN pip install pyaml
RUN pip install click
RUN pip install dateparser
