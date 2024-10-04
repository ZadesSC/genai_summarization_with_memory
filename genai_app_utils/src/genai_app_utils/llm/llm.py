# llm.py

import os
import logging
from genai_app_utils.utils.http_requests import make_http_request

# Define the LLM functions and configurations in a consolidated manner
def generate_llm_response(prompt, deployment_name, config, llm_model="azure", timeout=60):
    """
    Generate a response from the specified LLM model. Defaults to Azure LLM.

    Parameters:
        - prompt (str): The prompt to send to the LLM.
        - deployment_name (str): The deployment name or model to use.
        - config (Config): The configuration object holding LLM settings.
        - llm_model (str): The LLM provider/model to use ('azure', 'ollama', etc.).
        - timeout (int): The timeout for the HTTP request in seconds.
    """
    if llm_model == "azure":
        return generate_azure_llm_response(prompt, deployment_name, config, timeout)
    elif llm_model == "ollama":
        return generate_llm_response_ollama(prompt, deployment_name, config, timeout)
    else:
        logging.error(f"Unsupported LLM model: {llm_model}")
        return None


def generate_azure_llm_response(prompt, deployment_name, config, timeout=60):
    """
    Generate a response from the Azure LLM using the provided configuration.
    
    Parameters:
        - prompt (str): The prompt to send to the LLM.
        - deployment_name (str): The deployment name to use in Azure.
        - config (Config): Configuration object holding LLM and API settings.
        - timeout (int): The timeout for the HTTP request in seconds.
    
    Returns:
        - str: The response content from the Azure LLM, or None on error.
    """
    base_url = config.azure_openai_endpoint
    api_key = config.azure_openai_api_key
    api_version = config.openai_api_version

    payload = {
        "messages": [{"role": "system", "content": prompt}],
        "temperature": 0,
        "top_p": 0.95,
        "max_tokens": 2000
    }

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = make_http_request(
            url=f"{base_url}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}",
            method="POST",
            headers=headers,
            json_data=payload,
            return_type="json",
            timeout=timeout
        )

        if not isinstance(response, dict):
            raise ValueError(f"Unexpected response format: {response}")

        return response["choices"][0]["message"]["content"]

    except (ValueError, KeyError) as e:
        logging.error(f"Error generating response from Azure LLM: {e}")
        return None


def generate_llm_response_ollama(prompt, deployment_name, config, timeout=60):
    """
    Generate a response from the Ollama LLM using the provided configuration.

    Parameters:
        - prompt (str): The prompt to send to the LLM.
        - deployment_name (str): Not used in Ollama, kept for interface consistency.
        - config (Config): Configuration object holding LLM and API settings.
        - timeout (int): The timeout for the HTTP request in seconds.

    Returns:
        - str: The response content from the Ollama LLM, or None on error.
    """
    base_url = os.getenv("OLLAMA_URL", config.get("ollama_base_url", ""))
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "temperature": 0.1,
        "max_tokens": 2000
    }

    try:
        response = make_http_request(
            url=f"{base_url}/api/generate",
            method="POST",
            json_data=payload,
            return_type="json",
            timeout=timeout
        )

        if isinstance(response, dict):
            return response.get("response", "")
        else:
            raise ValueError(f"Unexpected response format: {response}")

    except (ValueError, KeyError) as e:
        logging.error(f"Error generating response from Ollama LLM: {e}")
        return None


def create_prompt(memories, query):
    """
    Create a formatted prompt using the memories and the query.
    
    Parameters:
        - memories (list): A list of memories to include in the prompt.
        - query (str): The query to which the LLM should respond.

    Returns:
        - str: The formatted prompt string.
    """
    prompt = f"You are an AI Assistant. You are given memories and a question. Use the memories to respond.\n"
    prompt += f"Question: {query}\nMemories:\n"
    for memory in memories:
        prompt += f"{memory}\n"
    return prompt
