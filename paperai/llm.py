import openai
from langchain import OpenAI
from langchain.llms.openai import BaseOpenAI
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel
from typing import List
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage


gpt_models_dict = {"gpt-35-turbo":"gpt-3.5-turbo",
                   "gpt-4_8k_ascent":"gpt-4-0314",
                   "gpt-4_32k_ascent":"gpt-4-32k-0314"}


def get_model(model_name:str) -> BaseOpenAI:
    if openai.api_type == "azure":
        return ChatOpenAI(engine=model_name, model_name=gpt_models_dict.get(model_name), temperature=0)
    return OpenAI(temperature=0.7)

class ChatLLM(BaseModel):

    llm:BaseOpenAI = None

    def __init__(self, model:str,**kwargs):
        super().__init__(**kwargs)
        self.llm = get_model(model)

    def generate(self, prompt: str, stop: List[str] = None) -> BaseOpenAI:
        return self.llm([HumanMessage(content=prompt)], stop=stop)