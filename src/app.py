import asyncio
import websockets
from handle_message import handle_message

async def socket_server(websocket):
    try:
        async for message in websocket:
            await handle_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        print("There was an error with the WebSocket connection")
    finally:
        print("Connection closed")
        await websocket.close()

async def main():
    async with websockets.serve(socket_server, "0.0.0.0", 9000):
        print("WebSocket server started on ws://localhost:9000")
        await asyncio.Future()  # Keeps the server running indefinitely

if __name__ == "__main__":
    asyncio.run(main())