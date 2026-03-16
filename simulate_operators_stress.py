import asyncio
import aiohttp
import random
from datetime import datetime

URL = "http://127.0.0.1:8000/jobcard/temp-submission/"  # your endpoint
NUM_OPERATORS = 500  # change this to 100 for next test

async def submit_operator(operator_id): 
    data = {
        "line": f"line{random.randint(1,3)}",
        "hour1": random.randint(0,12),
        "hour2": random.randint(0,12),
        "hour3": random.randint(0,12),
        "hour4": random.randint(0,12),
        "hour5": random.randint(0,12),
        "hour6": random.randint(0,12),
        "hour7": random.randint(0,12),
        "hour8": random.randint(0,12),
        "hour9": random.randint(0,12),
        "hour10": random.randint(0,12),
        "hour11": random.randint(0,12),
        "shift": random.choice(["Day","Night"]),
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, data=data) as resp:
                if resp.status == 200:
                    print(f"[{datetime.now().time()}] Operator {operator_id} submitted. Status: {resp.status}")
                else:
                    print(f"[{datetime.now().time()}] Operator {operator_id} FAILED. Status: {resp.status}")
    except Exception as e:
        print(f"[{datetime.now().time()}] Operator {operator_id} ERROR: {e}")

async def main():
    tasks = [submit_operator(i) for i in range(1, NUM_OPERATORS+1)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())