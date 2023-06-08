# Fusion Power Predator Parser
RUN LOCALLY:
    python main.py
    ARGS:
        --auto-parse - try to parse files automatically;
        --full-auto - fully auto mode, skipping all the files that couldn't parse automatically;
        --error-mode - error mode;
        -d - daemon mode, run parsing in the background. Requires Redis server and Celery worker;


PARSER COMMANDS:
	p - Skip folder
	l - Skip file
	o - Open file in EM
	n - ...
	d - Set delimiter
	e - Move to Error
	t - Move to Trash
	start - Start parsing


RUN DAEMON-MODE ON DOCKER:
    docker-compose run --rm parser python main.py *ARGS


RUN DAEMON-MODE LOCALL:
Requirements:
    Install and run Redis server: https://redis.io/docs/getting-started/installation/install-redis-on-windows/

RUN:
    1. Make sure that Redis server is running
    2. Start Celery worker: 'celery -A celery_parser worker --pool=solo -l info'
        (--pool-solo - workaround for starting celery on Windows)
    3. Start Parser with the key '-d'


WORKING WITH REDIS:
    Start server: 'sudo service redis-server start'
    Stop server: 'sudo service redis-server stop'
    Open redis-cli: 'redis-cli'
        - Flush all the keys: 'flushall'
        