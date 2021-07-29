# using the lightweight image as required (3.7-alpine)
FROM python:3.8.8

# define work dir
WORKDIR /usr/src/app/atb_exercise

# define volume (results folder) to get the new excel sheet
VOLUME /tmp/results /usr/src/app/results

# install ssh service (apk instead of apt since it's alpine image), rc tool
RUN apt update \
	&& apt install git

# clone Github repo
RUN git clone https://github.com/TonySchneider/atb_exercise .

# install python requirements
RUN python -m pip install -r requirements.txt

# run the supervisord
CMD ["python", "client.py"]