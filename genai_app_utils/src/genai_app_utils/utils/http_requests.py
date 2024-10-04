import requests

def make_http_request(url, method="GET", headers=None, params=None, data=None, json_data=None, return_type="json", timeout=60):
    """Make HTTP requests with support for different methods, headers, and return types."""
    try:
        method = method.upper()
        response = None

        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=headers, params=params, data=data, json=json_data, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, headers=headers, params=params, data=data, json=json_data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=timeout)
        else:
            return f"Error: Unsupported HTTP method '{method}'"

        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"

        if return_type == "json":
            return response.json()
        elif return_type == "text":
            return response.text
        elif return_type == "html":
            return response.content.decode('utf-8')
        elif return_type == "raw":
            return response.content
        else:
            return f"Error: Unsupported return type '{return_type}'"

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
