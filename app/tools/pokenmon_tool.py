import os
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type
from langchain_community.utilities import TavilySearchAPIWrapper
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

# (加载环境变量，例如使用 python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()

# 1. 定义工具的输入模型
class PokemonToolInput(BaseModel):
    pokemon_name: str = Field(description="The name of the Pokémon to search for.")

# 2. 定义核心工具
class PokemonInfoTool(BaseTool):
    name = "pokemon_info_retriever"
    description = "Searches online for a Pokémon's information and extracts its key attributes."
    args_schema: Type[BaseModel] = PokemonToolInput

    def _run(self, pokemon_name: str) -> dict:
        # 步骤 A: 搜索权威页面
        search = TavilySearchAPIWrapper()
        query = f"{pokemon_name} pokémon stats and abilities serebii or bulbapedia"
        search_results = search.results(query, max_results=1)
        
        if not search_results:
            return {"error": "Could not find information online."}
        
        url = search_results[0]['url']

        # 步骤 B: 加载网页内容
        loader = WebBaseLoader(url)
        docs = loader.load()
        page_content = docs[0].page_content

        # 步骤 C: 使用LLM提取信息
        llm = ChatOpenAI(model="gpt-4-turbo", temperature=0) # 强大的模型更适合提取
        
        parser = JsonOutputParser()

        prompt = PromptTemplate(
            template="""
            From the following HTML content, extract the specified attributes for the Pokémon '{pokemon_name}'.
            Return the information ONLY as a JSON object with the keys: 'attributes', 'abilities', 'base_stats', 'evolution_chain'.
            
            HTML Content:
            {page_content}
            
            JSON Output:
            """,
            input_variables=["pokemon_name", "page_content"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        chain = prompt | llm | parser
        
        try:
            extracted_info = chain.invoke({
                "pokemon_name": pokemon_name,
                "page_content": page_content[:15000] # 截断以避免超出上下文长度
            })
            return extracted_info
        except Exception as e:
            return {"error": f"Failed to extract information: {e}"}

    async def _arun(self, pokemon_name: str) -> dict:
        # 异步版本可以后续实现以提高性能
        raise NotImplementedError("pokemon_info_retriever does not support async")

