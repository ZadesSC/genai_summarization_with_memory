# **Memory Test Ultity*

The Memory Test Utility is a Python-based testing tool designed to evaluate the memory capabilities of the mem0 system with Large Language Models (LLMs). The primary function of this utility is to test how well different LLMs interact with mem0 to store and retrieve memories (statements), using customizable test cases.

## **Installation**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/genai_summarization_with_memory.git
   cd genai_summarization_with_memory

2. **Set up the virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # For Linux/MacOS
   venv\Scripts\activate       # For Windows

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Create a .env file: Set up environment variables in a .env file (such as API keys, endpoint URLs, etc.).**:
   Example:
   ```bash
   QDRANT_URL=http://localhost:6333
   QDRANT_PORT=6333
   AZURE_OPENAI_ENDPOINT=https://your-azure-openai-instance.openai.azure.com
   AZURE_OPENAI_API_KEY=your-openai-api-key
   OPENAI_API_VERSION=v1

## **Configuration**

**mem0 Configuration**: Customize the mem0 memory system using a configuration file (config.json). This file allows you to specify details like the LLM provider, model, and other settings for interacting with the memory system.

**Test Cases**: Test scenarios are provided via JSON files that define the memory operations (e.g., add, update, delete) and queries to be tested.

## **Usage**

You can either call the main.py file directory, or run it as a python program.
   ```bash
   python src/llm_memory_toolkit/main.py
   ```
 
Running it as a python program requires installing it first.
   ```bash
   pip install -e .
   python -m llm_memory_toolkit.main
   ```

You can run it direcly as a program
   ```bash
   pip install -e .
   llm_memory_toolkit
   ```

## **Running Test Cases**

Each test case will run the following steps:

1. Add statements to memory.
2. Query the memory to check if the statements were stored correctly.
3. Use mem0 to answer specific questions about the stored statements using the LLM.
4. Evaluate the LLM’s ability to process and return accurate answers based on stored memories.

### Test Case Example

    ```json
    {
        "test_name": "Simple Memory Test",
        "statements": [
            { "operation": "add", "content": "I went to Japan on March 2023" },
            { "operation": "add", "content": "I returned to the USA on April 2023" }
        ],
        "queries": [
            { "operation": "ask", "content": "When did I go to Japan?", "expected_answer": "March 2023" },
            { "operation": "ask", "content": "When did I return to the USA?", "expected_answer": "April 2023" }
        ]
    }
    ```





# Memory Addition with Different LLMs

This first experitment focuses on adding memories with different data types (string, integar, dates) using different LLMs (GPT4, GPT3.5, Llama3.1) and then evaluting the ability of the LLM to properly store and retrieve those data (memories).

Currently there are some issues with GPT3.5's ability to use mem0's tools so only GPT4 and Llama is tested.

## Test cases

For each category of data types, the following test will occur.
1. Statements will be added to memory using mem0
2. We will do a direct call on all memories to see if the statements in step 1 is properly stored in some form
3. We will use mem0's search feature to directly ask a specific question related to each memory.  The expectation is that the specific memory in question should be retrieved.  We will also send the quesiton and the memory to the LLM to see if it can answer the quesiton with the given memory.
4. We will ask a general question in regards to the states made in step 1, where the answer should contain all of the information in all the statments.  The expectation is that all the memories stored in step 1 should be returned.  The question and memory will also be send to the LLM to get a response.

# Results

The output for the above tests are stored in this folder.
You can see the llama result in the file llama_output_1.txt
You can see the gpt4 result in the file gpt4_output_1.txt


## Llama 3.1 Results

| Category  | Storage     | Query 1   | Query 2     |
|-----------|-------------|-----------|-------------|
| **Str**   | 1/10        | 1/10      | 1/10        |
| **Int**   | 3/10        | 3/10      | 3/10        |
| **Date**  | 2/10        | 2/10      | 2/10        |

Notes on Llama results
- Llama was able to use mem0 to store all 10 statements in memory, however it appears that llama considered the statements too similar and simply overwrote the previous statments, leaving only 1 memory of the 10 statements available in memory
- Due to the above, only Korean, the last statment that overwrote all overs, remain
- During the integer storing process, it seems to have duplicated entries instead and the actual correct statements were not stored
- We also see the first case of llama executing the tool from mem0 incorrectly, causing an error
- Dates were a huge problem for llama, whenever it tries to store dates it either causes errors or have duplicate entires

Llama 3.1 preformed very poorly due to its weaker model and lack of ability to understand and use tools effectively.  It often stored statements incorrectly, either overwritten existing statements or creating duplicated.  It also cannot handle using tools properly and often in cases will send incorrect commands, causing errors.

## GPT4 Results

| Category  | Storage     | Query 1   | Query 2     |
|-----------|-------------|-----------|-------------|
| **Str**   | 10/10       | 10/10     | 10/10       |
| **Int**   | 10/10       | 10/10     | 10/10       |
| **Date**  | 10/10       | 10/10     | 10/10       |

Notes on GPT4 results
- Unlike llama, for the str category, GPT4 was able to differiate the different languages as seperate memories and stored all 10 of them without a problem
- GPT4 then retrieved them without issues
- For the Int category, like the str category, GPT4 was able to store and retrieve the different test results with different tests correctly
- For dates, in some other runs, GPT4 was able to infer additional information from memory that were not explictly present in the original statements (eg. what dates did we come back to the United States. We only have one statement that directl said the date we came back to the United states, but have multiple that said we returned from another place.  GPT4 was able to deduce this from memory), however this was not consistant

GPT4 preformed very well, it understand the task and how to use the tools well and store and retrieved memories mostly correctly.


# Conclusion

Preformance of mem0 heavily depends on ho well the language model unstands and uses it.  Weaker models like llama have problems with using the mem0 tools and storing memories effectively, while stronger models like GPT4 preforms the task flawlessly.

Comparasion of llama an gpt4 results

| **Category**      | **Llama 3.1** | **GPT-4** |
|-------------------|---------------|-----------|
| **Str**           | 3/30          | 30/30     |
| **Int**           | 9/30          | 30/30     |
| **Dates**         | 6/30          | 30/30     |
| **Total**         | 18/90         | 90/90     |


# Memory Update with Different LLMs

For update, we will test with cases of increasing complexity and reasoning for each of the cateories.  This will be simplier in output compared to addition.  The Addition Tests might be rerun later with this new simplier format.  The tests contain only 10 tests per each of the 3 categories and its a simple pass/fail.

# Results

## GPT4 Results

| Category  | Storage     |
|-----------|-------------|
| **Str**   | 10/10       |
| **Int**   | 5/10        |
| **Date**  | 9/10        |

It appears that GPT4 have no issues with natural language questions but struggles more with questions related to numbers.