import subprocess
#import docker

from subprocess import Popen, PIPE

# docker container ps

# docker compose stop _container_
# docker compose start _container_


def main() :
    p = Popen(['docker', 'compose', 'up', '-d'])
    p = Popen(['docker', 'compose', 'down'])
    p = Popen(['docker', 'compose', 'stop', 'telegraf'])
    p = Popen(['docker', 'compose', 'start', 'telegraf'])


if __name__ == '__main__' :
        main()