from langchain_ollama import OllamaEmbeddings, ChatOllama, OllamaLLM

class OllamaModel():
    embeddings = None
    char = None
    def __init__(self, llm_model, embeddings_model, url, log):
        self.log = log
        self.log.info("\nOllamaModel.__init__()")
        self.chat = ChatOllama(model = llm_model, temperature =  0.8, top_p = 0.3, frequency_penalty = 0.4, presence_penalt = 0.95)
        self.llm = OllamaLLM(model = llm_model, token_max=1024, num_ctx=128000)
        self.embeddings = OllamaEmbeddings(model=embeddings_model, base_url=url)
    
    def summarizeArticles(self, question, context):
        self.log.info("\nOllamaModel.summarizeArticles()")
        self.log.debug("Question: " + str(question))
        self.log.debug("Context: " + str(context))

        prompt = f"""## SYSTEM ROLE
                    You are a chatbot designed to summarize and classify articles comming from RSS sources.
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
                    - If the answer cannot be found, explicitly state: "The provided context does not contain this information."

                    2. **Transparency**:
                    - Reference the articles title and link (in context) when providing information.
                    - Do not speculate or provide opinions.

                    3. **Clarity**:
                    - Use simple, professional, and concise language.
                    - Format your response in Markdown for readability.

                    ## TASK
                    1. Provide a summary of the relevant information in context related to user's question.
                    2. Point the user to relevant parts of the articles in context.
                    3. Provide the response in the following format:

                    ## RESPONSE FORMAT
                    '''
                    # [Headline sumarizing the topic]
                    [Brief summary of the events, clear text, use bulletpoints when possible]

                    **Source**:
                    • [[Title]([link])]
                    '''
                    """

        messages = [('user', prompt)]
        completion = self.chat.invoke(messages)

        return completion.content

    # TODO: Delete when getTopTopics works well
    def getTopTopics_old(self, articles):
        self.log.info("\nOllamaModel.getTopTopics()")
        self.log.debug("Articles: " + str(articles))

        result_format = """
            [{"topic": "[Write a headline that sumarizes the articles in the topic]",
             "articles": [{"article": "[article headline in context related to the topic]",
                           "link": "[article link in context]"]}]"""
        prompt = f"""## SYSTEM ROLE
                    You are a chatbot designed to identify and group the most relevant topics on a list of articles headlines.
                    Your answers must be based exclusively on provided content.

                    ## CONTEXT
                    Here is the relevant content:
                    '''
                    {str(articles)}
                    '''

                    ## GUIDELINES
                    1. **Accuracy**:
                    - Only use the content in the `CONTEXT` section to answer.
                    - Do not speculate, provide opinions or information outside of the `CONTEXT`.
                    - Provide only links present in the `CONTEXT`.
                    - Do not provide extra instructions.

                    2. **Clarity**:
                    - Use simple, professional, and concise language.
                    - Avoid special characters in topic name.
                    - Format your response in JSON.

                    ## TASK
                    1. Provide a list of the topics in the provided context
                    2. The list must be order based on relevancy (most frequent topics first)
                    3. Returno only a JSON without any extra comment.
                    4. Provide the response in the following format:
                    {result_format}
                    """

        messages = [('user', prompt)]
        completion = self.chat.invoke(messages)

        return completion.content

    def getTopTopics(self, articles):
        self.log.info("\nOllamaModel.getTopTopics()")
        self.log.debug("Articles: " + str(articles))

        result_format = """[{"topic": "[Unique topic title]", "summary": "[2 lines paragraph summarizing the topic]", "articles": ["link": "[article link in context]", ...}, ...]"""

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
                    - Avoid generic topic like 'Politics', 'Technology', 'Sports', 'Entretainment', 'Business', etc..
                    - All provided links must appear in the result.
                    - Do not provide topics without related articles.
                    - Do not speculate or provide opinions.
                    - Do not provide extra instructions.

                    2. **Clarity**:
                    - Use simple, professional, and concise language.
                    - Format your response in JSON.
                    - Do not add markdown indicatiors (eg.'```json ```') 

                    ## TASK
                    1. Provide a list of the topics in the provided context
                    2. The list must be order based on relevancy (topic with more realted articles first)
                    3. Return only a JSON without any extra comment.
                    4. Provide the answer in the following format:
                    {result_format}
                    """
        
        numTokInput = self.llm.get_num_tokens(str(articles))
        self.log.info("Num Tokens in Input: " + str(numTokInput))
        numTokPrompt = self.llm.get_num_tokens(str(prompt))
        self.log.info("Num Tokens in Prompt: " + str(numTokPrompt))

        self.log.debug("= PROMPT =================\n" + str(prompt) + "\n= END PROMPT =================")
        completion = self.llm.invoke(prompt)

        numTokCompletition = self.llm.get_num_tokens(completion)
        self.log.info("Num Tokens in Answer: " + str(numTokCompletition))

        return completion, numTokPrompt - numTokInput, numTokInput, numTokCompletition
