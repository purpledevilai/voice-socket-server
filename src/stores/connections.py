from models.AIVoiceChat import AIVoiceChat
from langchain_openai import ChatOpenAI
from models.AgentChatStream import AgentChatStream

connections = {}

def create_new_connection(context_id: str, websocket):
    llm = ChatOpenAI()
    connections[context_id] = AIVoiceChat(
        websocket=websocket,
        agent_chat_stream = AgentChatStream(llm, "you are a helpful assistant"),
        sample_rate = 16000
    )
