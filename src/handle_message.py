import json
from models.AIVoiceChat import AIVoiceChat
from stores.connections import connections, create_new_connection
from handlers.handle_audio_data import handle_audio_data
from handlers.handle_print_sample_rate import handle_print_sample_rate
from handlers.handle_create_wav_file import handle_create_wav_file


async def route_message(type: str, context_id: str, voice_chat: AIVoiceChat, data: dict):

    #################################################
    #
    #
    # -- Audio
    if (type == "audio"):
        await handle_audio_data(voice_chat, data)
    #
    #
    # -- Create wav file
    elif (type == "create_wav_file"):
        await handle_create_wav_file(data)
    #
    #
    # -- Invalid message type
    else:
        raise Exception(f"Invalid message type: {type}")
    #
    #
    #
    #####################################################


async def handle_message(websocket, message):
    try:
        # Parse the JSON message
        data = json.loads(message)

        # Get the message type
        type = data.get("type")
        if (type == None):
            raise Exception("No type provided")

        # Get the context ID
        context_id = data.get("context_id")
        if context_id == None:
            raise Exception("No context_id provided")

        # Check if context ID is in the connections dictionary
        if context_id not in connections:
            create_new_connection(context_id, websocket)

        # Get the voice chat instance
        voice_chat = connections[context_id]

        # Route message
        await route_message(type, context_id, voice_chat, data)

    except Exception as e:
        print(f"Error: {e}")
        await websocket.send(json.dumps({"error": str(e)}))
