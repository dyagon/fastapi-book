from pydantic import BaseModel, Field
from pprint import pprint

import os
from dotenv import load_dotenv
from typing import Any, Dict, Annotated, TypeVar

from pydantic import BaseModel, Field, model_validator

def _extract_and_strip_prefix(source: Dict, prefix: str) -> Dict[str, Any]:
    """
    A simple, non-recursive function to find keys with a prefix,
    strip that prefix, and return a new flat dictionary.
    
    Example:
    Input: {'ACCIO_KAFKA_CONSUMER_ID': '1', 'ACCIO_KAFKA_SSL_KEY': 'abc'}
    Prefix: 'ACCIO_KAFKA_'
    Output: {'consumer_id': '1', 'ssl_key': 'abc'}
    """
    prefix = prefix.upper()
    result = {}
    for key, value in source.items():
        key_upper = key.upper()
        if key_upper.startswith(prefix):
            clean_key = key_upper[len(prefix):]
            result[clean_key] = value
    return result


TSettings = TypeVar("TSettings", bound="PrefixedSettings")


class PrefixedSettings(BaseModel):
    """
    A base model that knows how to populate its children from prefixed env vars.
    """
    
    @model_validator(mode='before')
    @classmethod
    def _populate_prefixed_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        This validator runs before any other validation.
        It finds fields marked with a 'prefix' and populates them with a
        sub-dictionary of the environment variables.
        """
        populated_data = {}

        for field_name, field_info in cls.model_fields.items():
            print(field_name, field_info)
            # Check for our custom prefix metadata
            if field_info.json_schema_extra and 'prefix' in field_info.json_schema_extra:
                prefix = field_info.json_schema_extra['prefix']
                
                # Extract the relevant data from the source (os.environ)
                # and strip the prefix. This creates the clean dict the child model needs.
                sub_dict = _extract_and_strip_prefix(values, prefix)
                
                # Pydantic's internal logic will use this dict to create the nested model.
                populated_data[field_name] = sub_dict
            else:
                # For regular fields, just try to get them from the environment.
                # This handles 'AOAA_ORGANIZATION'.
                if field_name in values:
                     populated_data[field_name] = values[field_name]
        pprint(populated_data)
        return populated_data

    @classmethod
    def load(cls: TSettings, env_file: str = ".env") -> TSettings:
        """
        Class method to load from .env and environment, then validate.
        """
        load_dotenv(dotenv_path=env_file)
        # Pass the entire os.environ dictionary to the validator.
        return cls.model_validate(os.environ)



# This model is completely "dumb" - it only knows the shape of SSL settings.
# It has no idea about prefixes like ACCIO_KAFKA_SSL_
class SslSettings(BaseModel):
    KEYSTORE_DATA: str
    KEYSTORE_LOCATION: str
    KEYSTORE_PASSWORD: str
    KEY_PASSWORD: str
    TRUSTSTORE_DATA: str
    TRUSTSTORE_LOCATION: str
    TRUSTSTORE_PASSWORD: str
    model_config = { "from_attributes": True, "extra": "ignore" }

# This model is also "dumb". It just knows it needs a consumer group id,
# some servers, and an object that fits the SslSettings shape.
class KafkaSettings(PrefixedSettings):
    CONSUMER_GROUP_ID: str
    AUTO_STARTUP: bool = True
    BOOTSTRAP_SERVERS: str
    SCHEMA_REGISTRY_URL: str
    SCHEMA_REGISTRY_USER_INFO: str
    
    # The key here is that the field name 'ssl' matches the prefix
    # that our helper function will create from '..._SSL_...'
    SSL: Annotated[SslSettings, Field(..., prefix="SSL_")]
    model_config = { "from_attributes": True, "extra": "ignore" }


# --- Your ideal declarative structure ---
# Inherit from our new PrefixedSettings class
class AppSettings(PrefixedSettings):
    # Use the Prefixed() helper to tag the fields.
    # Pydantic will automatically call KafkaSettings(**data) where `data`
    # is the dictionary returned by our prefix-stripping logic.
    accio_kafka: Annotated[KafkaSettings, Field(..., prefix="ACCIO_KAFKA_")]
    aoo_kafka: KafkaSettings = Field(default_factory=KafkaSettings, prefix="AOAA_KAFKA_")

    # This is a regular field, our validator will pick it up by its name.
    AOAA_ORGANIZATION: str

    model_config = { "from_attributes": True, "extra": "ignore" }


def main():
    # The 'load' method orchestrates the entire process.
    settings = AppSettings.load()


    # print("--- ACCIO Kafka Config (Declarative Loading) ---")
    # print(f"Group ID: {settings.ACCIO_KAFKA.CONSUMER_GROUP_ID}")
    # print(f"Bootstrap Servers: {settings.ACCIO_KAFKA.BOOTSTRAP_SERVERS}")
    # print(f"SSL Keystore Location: {settings.ACCIO_KAFKA.SSL.KEYSTORE_LOCATION}")

    # print("\n--- AOAA Kafka Config (Declarative Loading) ---")
    # print(f"Organization: {settings.AOAA_ORGANIZATION}")
    # print(f"Group ID: {settings.AOAA_KAFKA.CONSUMER_GROUP_ID}")
    # print(f"Bootstrap Servers: {settings.AOAA_KAFKA.BOOTSTRAP_SERVERS}")
    # print(f"SSL Truststore Password: {settings.AOAA_KAFKA.SSL.TRUSTSTORE_PASSWORD}")

    # Pydantic's type conversion for the bool still works perfectly.
    # assert settings.AOAA_KAFKA.AUTO_STARTUP is True
    print("\nSuccessfully parsed settings with declarative model!")

if __name__ == "__main__":
    main()

