from langchain_ollama import OllamaEmbeddings, OllamaLLM

class OllamaModel():
    embeddings = None
    char = None
    def __init__(self, llm_model, embeddings_model, url, log):
        self.log = log
        self.log.info("\nOllamaModel.__init__()")
        self.llm = OllamaLLM(model = llm_model, token_max=1024, num_ctx=128000, temperature=0)
        self.embeddings = OllamaEmbeddings(model=embeddings_model, base_url=url)

    def summarizeArticles(self, question, context):
        self.log.info("\nOllamaModel.summarizeArticles()")
        self.log.debug("Question: " + str(question))
        self.log.debug("Context: " + str(context))

        result_format = '{"summary": "the summary of the content", "articles": ["article link in context", ...]}'
        prompt = f"""## SYSTEM ROLE
                    You are a chatbot designed to summarize and answer questions realted to information from RSS sources.
                    Your answers must be based exclusively on provided content.

                    ## USER QUESTION
                    The user has asked:
                    "{question}"

                    ## CONTEXT
                    Here is the relevant content from the RSS Sources:
                    '''
                    {context}
                    '''

                    ## GUIDELINES
                    1. **Accuracy**:
                    - Only use the content in the `CONTEXT` section to answer.
                    - If the answer cannot be found, explicitly state: "Not related articles found yet."
                    - The provided summary should cover all the available information.
                    
                    2. **Transparency**:
                    - Reference the articles link (in context) when providing information.
                    - Do not speculate or provide opinions.

                    3. **Clarity**:
                    - Use simple, professional, and concise language.
                    - Format your response in JSON.

                    ## TASK
                    1. Provide a summary of the relevant information in context related to user's question.
                    2. Point the user to relevant parts of the articles in context.
                    3. Return only a JSON without any extra comment.
                    4. Provide the answer following this JSON structure:
                    {result_format}
                    """
        
        numTokInput = self.llm.get_num_tokens(str(context))
        self.log.info("Num Tokens in Input: " + str(numTokInput))
        numTokPrompt = self.llm.get_num_tokens(str(prompt))
        self.log.info("Num Tokens in Prompt: " + str(numTokPrompt))

        self.log.debug("= PROMPT =================\n" + str(prompt) + "\n= END PROMPT =================")
        completion = self.llm.invoke(prompt)
        self.log.debug("= COMPLETION =================\n" + str(completion) + "\n= END COMPLETION =================")

        numTokCompletion = self.llm.get_num_tokens(completion)
        self.log.info("Num Tokens in Answer: " + str(numTokCompletion))

        # Guard Rails - Check JSON is well formated
        try:
            json.loads(completion)
        except:
            completion, numTokPrompt_json, numTokInput_json, numTokCompletion_json = self.fixJSON(completion, result_format)
            numTokPrompt += numTokPrompt_json
            numTokInput += numTokInput_json
            numTokCompletion += numTokCompletion_json

        return completion, numTokPrompt - numTokInput, numTokInput, numTokCompletion

    def getTopTopics(self, articles):
        self.log.info("\nOllamaModel.getTopTopics()")
        self.log.debug("Articles: " + str(articles))

        result_format = '[{"topic": "Unique topic title", "summary": "Multiple lines paragraph summarizing the topic", "articles": ["article link in context", ...]}, ...]'

        prompt = f"""## SYSTEM ROLE
                    You are a chatbot designed to identify and group the topics on a list of articles.
                    You must group articles covering similar topics and provide a brief summary about the topic.
                    You must also identify the topic relevancy based on quantity of related articles.
                    Your answers must be based exclusively on provided content.

                    ## CONTEXT
                    Here is the relevant content:
                    '''
                    {str(articles)}
                    '''

                    ## GUIDELINES
                    1. **Accuracy**:
                    - Only use the content in the `CONTEXT` section to answer.
                    - Topic must be between 1 and 4 words.
                    - Must avoid generic topic like 'Politics', 'Technology', 'Sports', 'Entretainment', 'Business', etc..
                    - Avoid word "and" in the topic.
                    - All provided links must appear in the result.
                    - Do not provide topics without related articles.
                    - Do not duplicate topics but group articles links with similar topic.
                    - Do not speculate or provide opinions.
                    - Do not provide extra instructions.

                    2. **Clarity**:
                    - Use simple, professional, and concise language.
                    - Format your response in JSON.

                    ## TASK
                    1. Provide a list of the topics in the provided context
                    2. Return only a JSON without any extra comment.
                    3. Provide the answer in the following format:
                    {result_format}
                    """
        
        numTokInput = self.llm.get_num_tokens(str(articles))
        self.log.info("Num Tokens in Input: " + str(numTokInput))
        numTokPrompt = self.llm.get_num_tokens(str(prompt))
        self.log.info("Num Tokens in Prompt: " + str(numTokPrompt))

        self.log.debug("= PROMPT =================\n" + str(prompt) + "\n= END PROMPT =================")
        completion = self.llm.invoke(prompt)
        self.log.debug("= COMPLETION =================\n" + str(completion) + "\n= END COMPLETION =================")

        numTokCompletion = self.llm.get_num_tokens(completion)
        self.log.info("Num Tokens in Answer: " + str(numTokCompletion))

        # Guard Rails - Check JSON is well formated
        try:
            json.loads(completion)
        except:
            completion, numTokPrompt_json, numTokInput_json, numTokCompletion_json = self.fixJSON(completion, result_format)
            numTokPrompt += numTokPrompt_json
            numTokInput += numTokInput_json
            numTokCompletion += numTokCompletion_json
    
        return completion, numTokPrompt - numTokInput, numTokInput, numTokCompletion

    def fixJSON(self, json, template):
        self.log.info("\nOllamaModel.fixJSON()")

        prompt = f"""## SYSTEM ROLE
                    You are an assistant focus on fixing JSON errors.
                    The user will provide you a JSON and an expected structure.
                    Your work is to ensure the JSON can be parsed and fits with the provided structure.

                    ## JSON
                    This is the JSON to fix:
                    '''
                    {json}
                    '''

                    ## GUIDELINES
                    1. **Accuracy**:
                    - Do not modify the data contained in the JSON to fix focus only on its structure.
                    - Respect as much as possible the JSON structure, just fix it.
                    - Do as less changes as possible in the JSON to fix.

                    2. **Clarity**:
                    - Format your response in JSON.
                    - JSON result must be parseable. 
                    - Put attention on closing all the JSON objects and lists.
                    - Do not add markdown indicatiors (eg.'```json ```') 
                    - Remove any character before and after the JSON.
                    - Do not provide alternatives, just one JSON.
                    - Resulting JSON must be parseable with python.

                    ## TASK
                    1. Fix the JSON code provided to make it parseable.
                    2. Return only the corrected JSON without any extra comment.
                    """
                    
        numTokInput = self.llm.get_num_tokens(str(json))
        self.log.info("Num Tokens in Input: " + str(numTokInput))
        numTokPrompt = self.llm.get_num_tokens(str(prompt))
        self.log.info("Num Tokens in Prompt: " + str(numTokPrompt - numTokInput))

        self.log.debug("= PROMPT =================\n" + str(prompt) + "\n= END PROMPT =================")
        completion = self.llm.invoke(prompt)
        self.log.debug("= COMPLETION =================\n" + str(completion) + "\n= END COMPLETION =================")

        numTokCompletion = self.llm.get_num_tokens(completion)
        self.log.info("Num Tokens in Answer: " + str(numTokCompletion))

        return completion, numTokPrompt, numTokInput, numTokCompletion