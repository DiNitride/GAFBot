import aiohttp

# Working aiohttp get_url
# Now with closing sessions!
# Ty Rory
async def get_url(url, ua):
    with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"user-agent" : ua}) as response:
            return response
