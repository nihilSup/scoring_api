
# About

Declarative api to describe fields with server-side validation. Also added basic web server to handle jsons by implementing reference api. Web api also has redis support. Implemented as homework task in OTUS python dev course. Main purpose to practice descriptors as fields in django style and inheritance stuff.

# How to use

```python
python -m scoring_api.api
```

There are two flagsFlag `-p, --port` to specify port for web server and `-l, --log` for log file path.

# Warning

* To work with clients_interests method you should start redis server with some content
* Desriptor fields will only work with python 3.6. For previous version one should use metaclass to handle descriptor names:

    ```python
    class NamedDescrMeta(type):
        def __init__(cls, name, bases, attrs):
            super().__init__(name, bases, attrs)
            for attr_name, attr_val in attrs:
                if isinstance(attr_val, Field):
                    attr_val.__set_name__(cls, attr_name)
    ```

    or support name to field via constructor

# How to test

```python
python -m unittest tests/integration/test_*.py
```

to run integration tests

```python
python -m unittest tests/unit/test_*.py
```

to run unit tests
