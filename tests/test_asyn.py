import asyncio
import httpx
import time

URLS = [
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/3",
    "https://httpbin.org/delay/1",
]

async def fetch(url):
    print(f"Start fetching: {url}")
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        print(f"Done fetching: {url}")
        return res.status_code

async def main():
    start = time.time()
    
    results = await asyncio.gather(*(fetch(url) for url in URLS))
    
    end = time.time()
    print(f"\nResults: {results}")
    print(f"Took {end - start:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())