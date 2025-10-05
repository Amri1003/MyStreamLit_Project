from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import Amri_Search
import streamlit as slt

load_dotenv()
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm= ChatOpenAI (model="gpt-4o-mini")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a research assistant. Given a research topic, you will provide a concise summary, list of sources, and tools used in the research. Format the output as per the ResearchResponse schema.\n{format_instructions}"
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [Amri_Search]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=[]
)
agent_exc = AgentExecutor(agent=agent,tools=[],verbose=True)

slt.subheader ("*** ANVESHI RESEARCH CENTRE ***")
query = slt.text_input("Welcome to the ANVESHI Research Assistant. Please enter your research topic: ")
if query:
    raw_response = agent_exc.invoke({"query": query})
    try:
          
        slt.write("Raw response:")
        slt.write(raw_response)
        # Extract and parse the output JSON string
        output_str = raw_response["output"]
        output_data = json.loads(output_str)

        # Display structured fields
        slt.write(f"**Topic:** {output_data['topic']}")
        slt.write(f"**Summary:** {output_data['summary']}")
        slt.write("**Sources:**")
        for source in output_data["sources"]:
            slt.write(f"- {source}")
        slt.write("**Tools Used:**")
        for tool in output_data["tools_used"]:
            slt.write(f"- {tool}")
    except Exception as e:
        print("Error parsing response:", e, "Raw Response", raw_response)
slt.caption (" If you have another query, just earse the above text and enter a new one(Its a workaround! I will work on it)")
slt.caption (" Thank you for using Amri Search .")

