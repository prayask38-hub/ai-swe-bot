import asyncio
import websockets
import json
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

connected_devices = {}

async def handle_command(command: str, device_id: str):
    print(f"\nCommand from {device_id}: {command}")

    if command.lower() in ["status", "ping"]:
        return {
            "status": "online",
            "device": device_id,
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "message": "AI SWE Bot is running"
        }

    elif command.lower().startswith("fix:"):
        code = command[4:].strip()
        return {
            "status": "processing",
            "message": "Analyzing code for bugs...",
            "code_received": len(code) > 0
        }

    elif command.lower().startswith("open:"):
        app = command[5:].strip()
        try:
            from smart_computer_use import run_task
            asyncio.create_task(
                asyncio.to_thread(run_task, f"open {app}")
            )
            return {
                "status": "executing",
                "message": f"Opening {app} on your PC"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    elif command.lower().startswith("ask:"):
        question = command[4:].strip()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": question}]
        )
        answer = response.choices[0].message.content
        return {
            "status": "success",
            "message": answer[:500]
        }

    elif command.lower().startswith("type:"):
        text = command[5:].strip()
        try:
            import pyautogui
            import time
            time.sleep(2)
            pyautogui.typewrite(text, interval=0.05)
            return {
                "status": "success",
                "message": f"Typed: {text}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    elif command.lower().startswith("hotkey:"):
        keys = command[7:].strip().split("+")
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            return {
                "status": "success",
                "message": f"Pressed: {'+'.join(keys)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    elif command.lower() == "screenshot":
        try:
            import pyautogui
            import base64
            from io import BytesIO
            screenshot = pyautogui.screenshot()
            buffer = BytesIO()
            screenshot.save(buffer, format="PNG")
            img_b64 = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")
            return {
                "status": "success",
                "message": "Screenshot taken",
                "screenshot": img_b64[:100] + "..."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    elif command.lower() == "list devices":
        return {
            "status": "success",
            "connected_devices": list(connected_devices.keys()),
            "total": len(connected_devices)
        }

    elif command.lower() == "stop":
        return {
            "status": "stopping",
            "message": "AI SWE Bot shutting down voice and tasks"
        }

    else:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"AI assistant command: {command}"}]
        )
        return {
            "status": "success",
            "message": response.choices[0].message.content[:300]
        }

async def handle_client(websocket):
    device_id = f"device_{len(connected_devices) + 1}"
    connected_devices[device_id] = websocket
    print(f"\nDevice connected: {device_id}")
    print(f"Total devices: {len(connected_devices)}")

    try:
        await websocket.send(json.dumps({
            "status": "connected",
            "device_id": device_id,
            "message": "Connected to AI SWE Bot",
            "commands": [
                "status — check if bot is online",
                "fix: <code> — analyze code for bugs",
                "open: <app> — open any app on PC",
                "ask: <question> — ask AI anything",
                "type: <text> — type text on PC",
                "hotkey: ctrl+s — press keyboard shortcut",
                "screenshot — take screenshot",
                "list devices — see connected devices",
                "stop — stop current task"
            ]
        }))

        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get("command", "")
            except:
                command = message

            response = await handle_command(command, device_id)
            await websocket.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        print(f"Device disconnected: {device_id}")
    finally:
        connected_devices.pop(device_id, None)

async def start_server(host: str = "0.0.0.0", port: int = 8765):
    print("=" * 40)
    print("  AI SWE Bot — Device Server")
    print("=" * 40)
    print(f"\nServer starting on port {port}...")

    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print(f"\nYour PC IP address: {local_ip}")
    print(f"Connect from any device on same WiFi:")
    print(f"  WebSocket URL: ws://{local_ip}:{port}")
    print(f"\nAvailable commands:")
    print("  status — check bot status")
    print("  fix: <code> — analyze code")
    print("  open: notepad — open any app")
    print("  ask: <question> — ask AI")
    print("  type: <text> — type on PC")
    print("  hotkey: ctrl+s — press shortcut")
    print(f"\nWaiting for devices to connect...")
    print("Press Ctrl+C to stop server.")

    async with websockets.serve(handle_client, host, port):
        await asyncio.Future()

def test_client():
    import asyncio

    async def connect_and_test():
        uri = "ws://localhost:8765"
        print(f"Connecting to {uri}...")

        async with websockets.connect(uri) as websocket:
            welcome = await websocket.recv()
            print(f"Server: {welcome}\n")

            commands = ["status", "ask: what is Python?", "list devices"]

            for cmd in commands:
                print(f"Sending: {cmd}")
                await websocket.send(json.dumps({"command": cmd}))
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Response: {data.get('message', data)}\n")
                await asyncio.sleep(1)

    asyncio.run(connect_and_test())

if __name__ == "__main__":
    print("1. Start device server")
    print("2. Test with local client")
    choice = input("\nChoose (1 or 2): ").strip()

    if choice == "1":
        asyncio.run(start_server())
    elif choice == "2":
        test_client()
