FROM python:3.8.8

# define work dir
WORKDIR /usr/src/app/atb_exercise

# update and install git
RUN apt update \
	&& apt install git

# clone Github repo
RUN git clone https://github.com/TonySchneider/atb_exercise .

# install python requirements
RUN python -m pip install -r requirements.txt

# run the supervisord
CMD ["python", "client.py"]