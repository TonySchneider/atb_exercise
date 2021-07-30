# ATB Exercise

## Requirements

* ubuntu 18.04 / 20.04 (stable version)
* docker service

## Docker hub image link:

* https://hub.docker.com/r/tonyschneider/atb_exercise_image

## How to pull and run the program?

```sh
docker pull tonyschneider/atb_exercise_image:latest
docker run -it --name atb_exercise -v /tmp/results:/usr/src/app/results tonyschneider/atb_exercise_image
```

![til](intro.gif)

## Authors

* **Tony Schneider** - *Programming* - [TonySchneider](https://github.com/tonySchneider)
