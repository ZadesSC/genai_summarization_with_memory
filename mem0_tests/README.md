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
