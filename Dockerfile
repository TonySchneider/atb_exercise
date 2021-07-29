# using the lightweight image as required (3.7-alpine)
FROM python:3.8.8

# define work dir
WORKDIR /usr/src/app

# define volume (results folder) to get the new excel sheet
VOLUME results /usr/src/app/results

# install ssh service (apk instead of apt since it's alpine image), rc tool
RUN apt update \
	&& apt install git

# clone Github repo
RUN git clone https://github.com/TonySchneider/atb_exercise

# install python requirements
RUN python -m pip install -r atb_exercise/requirements.txt

# run the supervisord
CMD ["python", "atb_exercise/client.py"]