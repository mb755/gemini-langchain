import configparser as cfg
import os
import json
import math
from utils.config_parser import default_parser

from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

###########################################################
# parse command line arguments
###########################################################

extraction_parser = default_parser(description="Save some marketdata to disk.")

args = vars(extraction_parser.parse_args())

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
# simple prompt to compare direct and processed results
###########################################################

# Initialize the Gemini model
llm = GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)


# Define the structure for the extracted information
class ExtractedInfo(BaseModel):
    initial_velocity: float = Field(description="Initial velocity of both cars in m/s.")
    initial_distance: float = Field(description="Distance between the two cars in m.")
    acceleration: float = Field(description="Acceleration of the rear car in m/s^2.")


class DirectAnswer(BaseModel):
    distance_travelled: float = Field(
        description="Distance travelled by the rear car before overtaking the front car in m."
    )


extraction_parser = PydanticOutputParser(pydantic_object=ExtractedInfo)
direct_parser = PydanticOutputParser(pydantic_object=DirectAnswer)

# Define the first prompt template for information extraction
extract_template = PromptTemplate(
    template="Extract the relevant physical quantities from the following text. {format_instructions}\n\nText: {text}\n",
    input_variables=["text"],
    partial_variables={
        "format_instructions": extraction_parser.get_format_instructions()
    },
)

direct_template = PromptTemplate(
    template="Answer the following question based on the provided information. {format_instructions}\n\nText: {text}\n",
    input_variables=["text"],
    partial_variables={"format_instructions": direct_parser.get_format_instructions()},
)

# Create the extraction chain
extract_step = extract_template | llm | extraction_parser

# Create the processing chain
direct_step = direct_template | llm | direct_parser


def distance_solver(extracted_info: ExtractedInfo):
    # Extract the information
    v0 = extracted_info.initial_velocity
    d0 = extracted_info.initial_distance
    a = extracted_info.acceleration

    # Calculate the time to overtake
    t = math.sqrt(2 * d0 / a)

    # Calculate the distance travelled
    d = v0 * t + 0.5 * a * t**2

    # Return the result
    return d


# Combine the chains
extract_chain = (
    RunnablePassthrough()
    | {"extracted_info": extract_step}
    | (lambda x: distance_solver(x["extracted_info"]))
)

direct_chain = (
    RunnablePassthrough()
    | {"direct_answer": direct_step}
    | (lambda x: x["direct_answer"].distance_travelled)
)

# prmopt
prompt_text = """
Two cars are travelling at a speed of 30 m/s along a highway. The rear one is 100m behind.
It starts accelerating at 1 m/s^2. How far does it travel before overtaking the car in front?
"""

# Run the chain
extraction_result = extract_chain.invoke(prompt_text)
direct_result = direct_chain.invoke(prompt_text)

print("Extracted Information (JSON format):")
extracted_info = extract_step.invoke(prompt_text)
print(json.dumps(extracted_info.model_dump(), indent=2))
print("\nFinal Summary and Analysis:")
print(extraction_result)

print("\nDirect Answer:")
print(direct_result)
