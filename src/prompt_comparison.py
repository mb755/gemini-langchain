import configparser as cfg
import os

from utils.config_parser import default_parser

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

###########################################################
# parse command line arguments
###########################################################

parser = default_parser(description="Save some marketdata to disk.")

args = vars(parser.parse_args())

output_suffix = args["output_suffix"]
config_file = args["config_file"]
overwrite = args["overwrite"]

###########################################################
# grab api key from config file and export to environment
###########################################################

config = cfg.ConfigParser()
config.read(config_file)

api_key = config.get("google", "api_key")
os.environ["GOOGLE_API_KEY"] = api_key

###########################################################
# parse command line arguments
###########################################################
