# Fusion Power Predator Parser

### RUN LOCALLY:
    python main.py
    ARGS:
        --auto-parse - try to parse files automatically;
        --full-auto - fully auto mode, skipping all the files that couldn't parse automatically;
        --error-mode - error mode;
        -d - daemon mode, run parsing in the background. Requires Redis server and Celery worker;


### PARSER COMMANDS:
	p - Skip directory
	l - Skip file
	o - Open file in EM
	n - Open in Notebook
	d - Set delimiter
	e - Move directory to Error
	t - Move directory to Trash
	start - Start parsing


### COLUMNS:
	um: usermail
	umn: user_mail_name
	uid: user_ID
	un: username
	ufn: user_fullname
	upp: userpass_plain
	s: salt
	h: hash
	t: tel
	c: city
	ip: ipaddress
	cn: country
	st: state
	a: address
	z: zip
	uai: user_additional_info
	p: password
	psp: passport
	dob: dob


### RUN DAEMON-MODE ON DOCKER:
    docker-compose run --rm parser python main.py *ARGS


### RUN DAEMON-MODE LOCAL

#### Requirements:
    Install and run Redis server: https://redis.io/docs/getting-started/installation/install-redis-on-windows/

#### RUN:
    1. Make sure that Redis server is running
    2. Start Celery worker: 'celery -A celery_parser worker --pool=solo -l info'
        (--pool-solo - workaround for starting celery on Windows)
    3. Start Parser with the key '-d'


#### WORKING WITH REDIS:
    Start server: 'sudo service redis-server start'
    Stop server: 'sudo service redis-server stop'
    Open redis-cli: 'redis-cli'
        - Flush all the keys: 'flushall'
        