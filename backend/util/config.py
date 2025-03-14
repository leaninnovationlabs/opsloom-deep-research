import configparser
import os
import dotenv

# TODO: Need to do this 
dotenv.load_dotenv()

config = configparser.ConfigParser()
config.read(f'backend/config/{os.getenv("ENV")}-config.ini')

def get_config():
    config = configparser.ConfigParser()
    env = os.getenv("ENV", "dev")  # Default to 'dev' if ENV is not set

    # Construct the absolute path to the config file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, '..', 'config', f'{env}-config.ini')
    filename = os.path.abspath(filename)

    # Check if the file exists
    if os.path.exists(filename):
        config.read(filename)
    else:
        print(f"Config file {filename} does not exist")

    return config

def get_config_value(key):

    if key in config['app.config']:
        return config['app.config'][key]
    else:
        return os.getenv(key)
