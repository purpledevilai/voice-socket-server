import asyncio
import websockets

print("Hello from app.py")

# A simple WebSocket server that echoes back received messages
async def echo(websocket, path):
    print("Client connected!")
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # Echo the message back to the client
            await websocket.send(f"Echo: {message}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Client disconnected unexpectedly: {e}")
    except websockets.exceptions.ConnectionClosedOK as e:
        print(f"Client disconnected gracefully: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Connection closed.")

# Start the WebSocket server
start_server = websockets.serve(echo, "0.0.0.0", 8765)

print("WebSocket server started on ws://0.0.0.0:8765")

# Run the server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
