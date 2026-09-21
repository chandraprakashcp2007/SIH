"""Measured concurrent load harness for deterministic PRAHARI Copilot queries."""
import asyncio
import statistics
import time
import httpx

BASE_URL = "http://127.0.0.1:8000"
QUERIES = ["How is the system?", "jala status", "gateway okay ah", "alert ethavathu iruka", "highest risk"] * 20


def percentile(values, pct):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round((len(ordered) - 1) * pct)))]


async def main():
    async with httpx.AsyncClient(timeout=20.0) as client:
        auth = await client.post(f"{BASE_URL}/api/auth/login", json={"username": "operator", "password": "benchmark"})
        auth.raise_for_status()
        headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}
        semaphore = asyncio.Semaphore(10)
        async def ask(query):
            async with semaphore:
                started = time.perf_counter()
                response = await client.post(f"{BASE_URL}/api/copilot/chat", headers=headers, json={"message": query})
                return (time.perf_counter() - started) * 1000, response.status_code, bool(response.json().get("answer")) if response.status_code == 200 else False
        started = time.perf_counter()
        results = await asyncio.gather(*(ask(query) for query in QUERIES))
    latencies = [item[0] for item in results]
    errors = sum(1 for _, status, answered in results if status != 200 or not answered)
    print(f"Requests: {len(results)} | Elapsed: {time.perf_counter()-started:.2f}s | Error rate: {errors/len(results)*100:.2f}%")
    print(f"p50={percentile(latencies,.50):.2f}ms p95={percentile(latencies,.95):.2f}ms p99={percentile(latencies,.99):.2f}ms mean={statistics.mean(latencies):.2f}ms")


if __name__ == "__main__":
    asyncio.run(main())
