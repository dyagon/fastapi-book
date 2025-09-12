# misc


## how to config

```python
class AppSettings(BaseSettings):
    db: DatabaseSettings
    server: ServerSettings
    db2: DatabaseSettings
```

use `env_nested_delimiter` to configure the nested model.

otherwise, you need to handle the nested model manually, like config.py does. In this way, you may encounter the issue that the type hint is not working.
