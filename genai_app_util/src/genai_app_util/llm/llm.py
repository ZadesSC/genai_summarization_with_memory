import logging
from src.utils.http_requests import make_http_request  # Updated import

# Hard code to azure for now, most likley change, add more other LLMs later
def generate_llm_response(prompt, deployment_name, config):
    """Generate a response from the Azure LLM."""
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
            return_type="json"
        )

        if not isinstance(response, dict):
            raise ValueError(f"Unexpected response format: {response}")

        return response["choices"][0]["message"]["content"]

    except (ValueError, KeyError) as e:
        logging.error(f"Error generating response from Azure LLM: {e}")
        return None
