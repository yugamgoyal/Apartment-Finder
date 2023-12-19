Our Jira Board: https://apart-finder.atlassian.net/jira/software/projects/AF/boards/1 

Onboarding: 

    Front-End: React Based
    ---------------------------------------------------------------

    Back-End: (coming from a MacOS intel chip user)
    ---------------------------------------------------------------
        - Flask Setup:
            - cd flask-server
            - pip3 install virtualenv
            - python3 -m venv myenv
            - source myenv/bin/activate
            - pip3 install -r requirements.txt

        - Redis Setup:
            - Open a new terminal
            - brew --version (ensure brew is installed)
            - brew install redis
            - redis-server (start the server)
                - Test the connection with server
                    - Open a new terminal and follow the following commands
                        - ensure the server is still running (needs to be runnging the entire time)
                        - redis-cli
                        - ping
                        - output: you shouls see "PONG"

        - Enviroment Setup:
            - touch .env
            - SECRET_KEY = any set of random keys
            - SQLALCHEMY_DATABASE_URI = sqlite:///./dbsqlite
            - SESSION_REDIS_URL = This should be what shows up when you do redis-cli (example: redis://127.0.0.1:6379)
            - MAIL_USERNAME = "yug.goyal46@gmail.com"
            - MAIL_PASSWORD = Contact me for the password
            - BASE_URL = Whatever flask server is running on

        - Running the sever:
            - python3 server.py

        Should be able to run server.py and start testing endpoints




