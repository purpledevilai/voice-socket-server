from models.AIVoiceChat import AIVoiceChat

connections = {}

def create_new_connection(context_id: str, websocket):
    connections[context_id] = AIVoiceChat(
        websocket=websocket,
        sample_rate=16000
    )
