import configparser
import os

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def test_read_api_key():
    config = configparser.ConfigParser()
    config.read(f"{root_dir}/config/default-api-keys.ini")

    assert "google" in config, "Section 'google' not found in config file"
    assert "api_key" in config["google"], "Key 'api_key' not found in section 'google'"
    assert (
        config["google"]["api_key"] == "dummy_key"
    ), "API key value does not match expected 'dummy_key'"
