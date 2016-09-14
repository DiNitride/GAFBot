import aiohttp

# Working aiohttp get_url
# Now with closing sessions!
# Ty Rory
async def get_url(url, ua):
    with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"user-agent" : ua}) as response:
            status = response.status
            if status != 200:
                json = None
                return response, json, status
            json = await response.json()
            return response, json, status
