# About:
Declarative api to describe fields with server-side validation. Also added basic web server to handle jsons by implementing reference api. Web api also has redis support. Implemented as homework task in OTUS python dev course. Main purpose to practice descriptors as fields in django style and inheritance stuff.

# How to use:
```python -m scoring_api.api```

There are two flagsFlag `-p, --port` to specify port for web server and `-l, --log` for log file path. 

# Warning:
Also to work with clients_interests method you should start redis server with some content

# How to test:
```python -m unittest tests/integration/test_*.py``` to run integration tests
```python -m unittest tests/unit/test_*.py``` to run unit tests