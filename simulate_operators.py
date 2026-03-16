import asyncio
import aiohttp  # async HTTP requests
import random

# URL of your temp submission endpoint
URL = "http://127.0.0.1:8000/jobcard/temp-submission/"

# Number of operators to simulate
NUM_OPERATORS = 20

# Example operator data (modify keys to match your form fields)
def generate_data():
    return {
        "line": f"Line{random.randint(1,3)}",
        "hour1": random.randint(0, 12),
        "hour2": random.randint(0, 12),
        "hour3": random.randint(0, 12),
        "hour4": random.randint(0, 12),
        "hour5": random.randint(0, 12),
        "hour6": random.randint(0, 12),
        "hour7": random.randint(0, 12),
        "hour8": random.randint(0, 12),
        "hour9": random.randint(0, 12),
        "hour10": random.randint(0, 12),
        "hour11": random.randint(0, 12),
        "shift": random.choice(["Day", "Night"]),
        "csrfmiddlewaretoken": "dummy",  # Django ignores if using @csrf_exempt for testing
    }

async def submit_operator(session, operator_id):
    data = generate_data()
    async with session.post(URL, data=data) as resp:
        text = await resp.text()
        print(f"Operator {operator_id} submitted. Status: {resp.status}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [submit_operator(session, i+1) for i in range(NUM_OPERATORS)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())