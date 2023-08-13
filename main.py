import asyncio
import websockets
import ssl, pathlib # wss secure dependencies

#import keepalive
#thread1 = keepalive.thread("pingendpt", 4881)
#thread1.run(4881) f

connections = []
channels = {}

async def announce(wsobj, msg):
    global connections, channels
    channel = channels[wsobj]

    for i in connections:
        if channels[i] == channel: #if relevant channel matches that of the element
            await i.send(f'{msg}:{hex(id(wsobj))}')
    
async def echo(websocket):
    global connections
    global channels
    async for message in websocket:
        #print(websocket)
        print(message[0:20])
        try:
            cmd = message[0:2]
            channel = message[2:6]
            params = message[6:]
        except:
            cmd = 'NO'
            params = '<NULL>'

        if cmd == 'NO':
            pass # do nothing command
        elif cmd == 'DB':
            await websocket.send(f"{channels}\n\n\n{connections}")
        elif cmd == 'CN':
            await websocket.send(f'OK{channel}{hex(id(websocket))}')
            connections.append(websocket)
            channels[websocket] = channel
            print(f'Added {websocket} to array with channel {channels[websocket]}.')
            #await announce(websocket, 'HELLO')
            #the handler should not transfer control away at any point or connection will close prematurely
            for i in connections:
                if channels[i] == channel: 
                    try: await i.send(f'NU{channel}{hex(id(websocket))} {params}')
                    except:
                        #await i.close()
                        connections.remove(i)
                        print(f'Dropped {websocket} due to unreachable host.')
                        #await announce(i, 'DIED')
                        pass
        elif cmd == 'DN':
            await connections[connections.index(websocket)].close()
            connections.remove(websocket)
            print(f'Dropped {websocket} at user request.')
            #await announce(websocket, 'BYE')
            for i in connections:
                if channels[i] == channel: 
                    try: await i.send(f'DU{channel}{hex(id(websocket))} {params}')
                    except:
                        #await i.close()
                        connections.remove(i)
                        print(f'Dropped {websocket} due to unreachable host.')
                        #await announce(i, 'DIED')
                        pass
        elif cmd == 'RN':
            await websocket.send(f'OK{channel}{hex(id(websocket))}')
            channels[websocket] = params
            print(f'Reassigned {websocket} to array with channel {channels[websocket]}.')
            #await announce(websocket, 'HELLO')
            #print(channels)
            #the handler should not transfer control away at any point or connection will close prematurely
            for i in connections:
                try:
                    if channels[i] == channel: 
                        try: await i.send(f'DU{channel}{hex(id(websocket))} {params}')
                        except:
                            #await i.close()
                            connections.remove(i)
                            print(f'Dropped {websocket} due to unreachable host.')
                            #await announce(i, 'DIED')
                            pass
                    if channels[i] == params: 
                        try: await i.send(f'NU{channel}{hex(id(websocket))} {params}')
                        except:
                            #await i.close()
                            connections.remove(i)
                            print(f'Dropped {websocket} due to unreachable host.')
                            #await announce(i, 'DIED')
                            pass
                except:
                    pass
                        
        else: #relay non commands
            #print(message)
            for i in connections:
                if channels[i] == channel and i != websocket:
                    try: 
                        await i.send(message) # if the connobj channel is the current channel
                        print("Relayed to "+str(websocket))
                    except:
                        #await i.close()
                        connections.remove(i)
                        print(f'Dropped {websocket} due to unreachable host.')
                        #await announce(i, 'DIED')
                      
                        
                       
                        
                      

                   
                    #if unreachable, we try to close it then delete the obj. if that doesn't work then just delete the object

async def main():
    print('Starting ws server on port TCP:443')

    #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #ssl_context.load_cert_chain(certfile="twocert.crt", keyfile="private.key")

    #ssl_context.options |= ssl.OP_NO_TLSv1
    #ssl_context.options |= ssl.OP_NO_TLSv1_1
    
    #localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
    #ssl_context.load_cert_chain(localhost_pem)

   
    async with websockets.serve(echo, "", 443, ping_interval=None):
        await asyncio.Future()  # run forever

asyncio.run(main())
