import subprocess
import asyncio


async def run_unilinear2():
    process = await asyncio.create_subprocess_shell(
        'sudo python3 mnoptical/examples/unilinear2.py 100 15 10 15 0.05 test', 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = await process.communicate()

    if process.returncode == 0:
        print('Done.')
    else:
        print('Error.')

asyncio.run(run_unilinear2())