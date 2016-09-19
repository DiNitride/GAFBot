import aiohttp

# Working aiohttp get_url
# Now with closing sessions!
# Ty Rory

async def get_url(url, headers: dict = None):
    headers = headers or {"user-agent" : "GAF Bot"}
    with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            status = response.status
            if status != 200:
                json = None
                return response, json, status
            json = await response.json()
            return response, json, status

async def post_url(url, data: dict = None, headers: dict = None):
    headers = headers or {"user-agent": "GAF Bot"}
    with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            status = response.status
            if status != 200:
                json = None
                return response, json, status
            json = await response.json()
            return response, json, status

