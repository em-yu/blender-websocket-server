#!/usr/bin/env python

import asyncio
import json
import os
import ssl
import time
from datetime import datetime
from typing import List, Tuple

import numpy as np
import websockets


try:
    width = os.get_terminal_size().columns 
except:
    width = 20

async def send_message(
        websocket,
        message): 

    await websocket.send(
        json.dumps(message))


async def handle_exception(websocket, error_message, status="ERROR"):
    print("Error:", error_message)
    message = {
                "status": status,
                "message": error_message
            }
    
    await websocket.send(
        json.dumps(
            message
        ))

async def handler(websocket):

    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosedOK:
            print("Closed connection.")
            break
        except websockets.exceptions.ConnectionClosedError:
            print("Closed connection.")
            break
        # async for message in websocket:
        print("=" * width)
        print("Received websocket message.")

        print(message)

        try:
            data = json.loads(message)

            try:
                action = data["action"]

                if action == 0:
                    print("Handling request (random number)")
                    x = np.random.rand()
                    y = np.random.rand()
                    z = np.random.rand()
                    await send_message(websocket, {'x': x, 'y': y, 'z': z})

            except Exception as e:
                await handle_exception(websocket, "Malformed input message. " + str(e))
                continue

        except Exception as e:
            await handle_exception(websocket, "Malformed input message. " + str(e))
            continue



        # print(f"Requested action = {action}")




async def main():
    print("Starting backend server. Waiting for websocket messages... (Press Ctrl + C to quit)")
    async with websockets.serve(handler, "", 5001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
