import asyncio
import websockets
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer

# ICE servers for WebRTC
iceServers = [
    {
        "urls": "stun:stun.relay.metered.ca:80",
    },
    # {
    #     "urls": "turn:global.relay.metered.ca:80",
    #     "username": "854bc4758e20cfe78cf64c95",
    #     "credential": "+KBw1GxPiZBSkrmt",
    # },
    # {
    #     "urls": "turn:global.relay.metered.ca:80?transport=tcp",
    #     "username": "854bc4758e20cfe78cf64c95",
    #     "credential": "+KBw1GxPiZBSkrmt",
    # },
    # {
    #     "urls": "turn:global.relay.metered.ca:443",
    #     "username": "854bc4758e20cfe78cf64c95",
    #     "credential": "+KBw1GxPiZBSkrmt",
    # },
    # {
    #     "urls": "turns:global.relay.metered.ca:443?transport=tcp",
    #     "username": "854bc4758e20cfe78cf64c95",
    #     "credential": "+KBw1GxPiZBSkrmt",
    # },
]

connections = {}

def parse_ice_candidate(candidate_str, sdpMid=None, sdpMLineIndex=None):
    # Split the candidate string into components
    parts = candidate_str.split()

    if not parts[0].startswith("candidate:"):
        raise ValueError("Invalid ICE candidate format")

    foundation = parts[0].split(":")[1]
    component = int(parts[1])
    protocol = parts[2]
    priority = int(parts[3])
    ip = parts[4]
    port = int(parts[5])

    # Find the candidate type
    type_index = parts.index("typ") + 1
    candidate_type = parts[type_index]

    # Find relatedAddress and relatedPort if they exist
    relatedAddress = None
    relatedPort = None
    if "raddr" in parts:
        related_index = parts.index("raddr") + 1
        relatedAddress = parts[related_index]
        relatedPort = int(parts[related_index + 2]
                          ) if "rport" in parts else None

    # Find tcpType if present
    tcpType = None
    if "tcptype" in parts:
        tcp_index = parts.index("tcptype") + 1
        tcpType = parts[tcp_index]

    # Construct RTCIceCandidate object
    return RTCIceCandidate(
        foundation=foundation,
        component=component,
        protocol=protocol,
        priority=priority,
        ip=ip,
        port=port,
        type=candidate_type,
        relatedAddress=relatedAddress,
        relatedPort=relatedPort,
        sdpMid=sdpMid,
        sdpMLineIndex=sdpMLineIndex,
        tcpType=tcpType
    )

async def handle_candidate(websocket, data):
    # Context ID
    context_id = data.get("context_id")
    if context_id == None:
        raise Exception("No context_id provided")
    
    # Candidate
    candidate_data = data.get("candidate")
    if candidate_data == None:
        raise Exception("No candidate provided")
    
    # Get the peer connection
    pc = connections.get(context_id)
    if pc == None:
        raise Exception("No peer connection found")
    
    # Parse the candidate
    candidate = parse_ice_candidate(
        candidate_data.get("candidate"),
        candidate_data.get("sdpMid"),
        candidate_data.get("sdpMLineIndex")
    )

    await pc.addIceCandidate(candidate)

def create_new_peer_connection(context_id, websocket):
    # Create a new peer connection
    ice_server_objects = [RTCIceServer(**server) for server in iceServers]
    configuration = RTCConfiguration(iceServers=ice_server_objects)
    pc = RTCPeerConnection(configuration=configuration)
    connections[context_id] = pc

    # Add a dummy data channel to trigger ICE candidate gathering
    channel = pc.createDataChannel("chat")

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(f"Data channel created: {channel.label}")

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print(f"ICE connection state is: {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed":
            await pc.close()
            print("Connection failed")

    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate:  # Ensure candidate is not None
            print("Sending ICE candidate")
            await websocket.send(json.dumps({
                "type": "candidate",
                "candidate": {
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex
                }
            }))
        else:
            print("End of ICE candidates")

    return pc

async def handle_offer(websocket, data):
    print("Handling offer")

    # Context ID
    context_id = data.get("context_id")
    if context_id == None:
        raise Exception("No context_id provided")
    
    # Offer
    offer_data = data.get("offer")
    if offer_data == None:
        raise Exception("No offer provided")
    offer = RTCSessionDescription(sdp=offer_data["sdp"], type=offer_data["type"])

    # Create a new peer connection
    pc = create_new_peer_connection(context_id, websocket)
    
    # Set the remote description
    await pc.setRemoteDescription(offer)

    # Create an answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Send the answer
    await websocket.send(json.dumps({
        "type": answer.type,
        "sdp": answer.sdp
    }))
    print("Answer sent")

async def handle_message(websocket, message):
    try:
        data = json.loads(message)
        type = data.get("type")
        if (type == None):
            raise Exception("No type provided")
        
        if (type == "offer"):
            await handle_offer(websocket, data)
        elif (type == "candidate"):
            await handle_candidate(websocket, data)
        else:
            raise Exception(f"Invalid message type: {type}")

    except Exception as e:
        print(f"Error: {e}")
        await websocket.send(json.dumps({"error": str(e)}))


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
