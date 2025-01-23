""" This module is used to interact with the  LLM using the langchain library. """

import os
from typing import List

from dotenv import load_dotenv
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
import logging
# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Ensure environmental variables are loaded
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(temperature=0, api_key=openai_api_key, model="gpt-4o")

def supreme_text_agent(prompt: str) -> dict:
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """

    # Create a PromptTemplate object
    prompt = PromptTemplate(
        template=prompt,
    )

    chain = prompt | model

    response = chain.invoke({})

    return response.dict()

def supreme_agent(agent_query: str, context: str, output_parser: PydanticOutputParser) -> dict:
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """
    prompt = PromptTemplate(
        template="You are an expert in information extraction from markdown text. Always answer the user query in JSON format.\n{format_instructions}\n{query}\n. The context is {context}",
        input_variables=["context", "query"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    chain = prompt | model | output_parser

    result = chain.invoke({"context": context, "query": agent_query})

    print(f"Result: {result}")

    return result.dict()

def supreme_vision_agent(image_urls: List[str], system_prompt: str) -> dict:
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """

    results = []
    with get_openai_callback() as cb:
        for i in range(0, len(image_urls), 2):
            batch = image_urls[i:i + 2]

            print(f"Processing batch: {len(batch)}")

            if len(batch) == 2:
                images_data = [
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,{image_url_1}"}
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,{image_url_2}"}
                    }
                    ]

                # Create the prompt template based on the number of images in the batch
                prompt_messages = [
                    ("system", system_prompt),
                    ("user", images_data),
                ]

                prompt = ChatPromptTemplate.from_messages(prompt_messages)

                # Build the processing chain
                chain = prompt | model


                # Prepare the invocation parameters
                result = chain.invoke({"image_url_1": batch[0], "image_url_2": batch[1]})
                results.append(result.content)
            else:
                print("Processing single image")
                images_data = [
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,{image_url_1}"}
                    }
                ]

                # Create the prompt template based on the number of images in the batch
                prompt_messages = [
                    ("system", system_prompt),
                    ("user", images_data),
                ]

                prompt = ChatPromptTemplate.from_messages(prompt_messages)


                # Build the processing chain
                chain = prompt | model 

                # Prepare the invocation parameters
                result = chain.invoke({"image_url_1": batch[0]})
                results.append(result.content)

        input_token_cost = 0.000005
        completion_token_cost = 0.000015
        # Print the total token usage and cost
        print(f"Total Tokens Used: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Input Token Cost (USD): ${cb.total_tokens * input_token_cost:.6f}")
        print(f"Completion Token Cost (USD): ${cb.completion_tokens * completion_token_cost:.6f}")
        print(f"Total Cost Input + Completion (USD): ${cb.total_tokens * input_token_cost + cb.completion_tokens * completion_token_cost:.6f}")

    return results


def supreme_vision_agent_one_img(image_url: str, system_prompt: str) -> dict:
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """

    results = []
    with get_openai_callback() as cb:
        images_data = [
            {
                "type": "image_url",
                "image_url": {"url": "data:image/jpeg;base64,{image_url}"}
            }
        ]

        # Create the prompt template based on the number of images in the batch
        prompt_messages = [
            ("system", system_prompt),
            ("user", images_data),
        ]

        prompt = ChatPromptTemplate.from_messages(prompt_messages)


        # Build the processing chain
        chain = prompt | model 

        # Prepare the invocation parameters
        result = chain.invoke({"image_url": image_url})
        results.append(result.content)

        input_token_cost = 0.000005
        completion_token_cost = 0.000015
        # Print the total token usage and cost
        print(f"Total Tokens Used: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Input Token Cost (USD): ${cb.total_tokens * input_token_cost:.6f}")
        print(f"Completion Token Cost (USD): ${cb.completion_tokens * completion_token_cost:.6f}")
        print(f"Total Cost Input + Completion (USD): ${cb.total_tokens * input_token_cost + cb.completion_tokens * completion_token_cost:.6f}")

    return results