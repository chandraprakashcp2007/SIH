"""
PRAHARI-NET Stress & Benchmark Harness
Sends 1,000+ telemetry records across simulated nodes, measures latency, throughput, and error rates.
"""
import time
import asyncio
import httpx
import statistics

BASE_URL = "http://127.0.0.1:8000"
INGEST_URL = f"{BASE_URL}/api/telemetry/ingest"
NUM_PACKETS = 1000


def percentile(values, pct):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * pct))))]


async def run_stress_benchmark():
    print(f"==================================================")
    print(f"PRAHARI-NET High-Throughput Ingestion Benchmark")
    print(f"Target: {INGEST_URL} | Packets: {NUM_PACKETS}")
    print(f"==================================================")

    latencies_ms = []
    errors = 0
    start_total = time.perf_counter()

    nodes = ["JALA-01", "AGNI-02", "BHUMI-03"]

    async with httpx.AsyncClient(timeout=10.0) as client:
        auth = await client.post(f"{BASE_URL}/api/auth/login", json={"username": "gateway", "password": "benchmark"})
        auth.raise_for_status()
        headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}
        # Check server availability first
        try:
            health = await client.get(f"{BASE_URL}/api/system/health", headers=headers)
            if health.status_code != 200:
                print("Server is not healthy.")
                return
        except Exception as e:
            print(f"Cannot connect to backend: {e}. Ensure backend is running.")
            return

        for seq in range(1, NUM_PACKETS + 1):
            node_id = nodes[seq % 3]

            if node_id == "JALA-01":
                metrics = {
                    "water_level_cm": 35.0 + (seq % 40) * 0.5,
                    "water_rise_rate_cm_min": 0.4,
                    "water_rise_acceleration": 0.01,
                    "rain_intensity": 5.0,
                    "temperature_c": 28.0
                }
            elif node_id == "AGNI-02":
                metrics = {
                    "mq2_raw": 120.0 + (seq % 50),
                    "mq135_raw": 135.0,
                    "temperature_c": 27.0,
                    "flame_detected": False,
                    "camera_fire_confidence": 0.0
                }
            else:
                metrics = {
                    "soil_moisture_upper_pct": 30.0 + (seq % 30) * 0.5,
                    "soil_moisture_lower_pct": 35.0,
                    "tilt_delta_deg": 0.15,
                    "vibration_rms": 0.5,
                    "rain_context": 6.0
                }

            payload = {
                "version": 1,
                "node_id": node_id,
                "sequence": 1000 + seq,
                "metrics": metrics,
                "rssi": -75,
                "battery_pct": 95.0,
                "is_simulation": True
            }

            t0 = time.perf_counter()
            try:
                resp = await client.post(INGEST_URL, json=payload, headers=headers)
                t1 = time.perf_counter()
                if resp.status_code == 200:
                    latencies_ms.append((t1 - t0) * 1000.0)
                else:
                    errors += 1
            except Exception:
                errors += 1

            if seq % 200 == 0:
                print(f"Processed {seq}/{NUM_PACKETS} packets...")

    total_duration_sec = time.perf_counter() - start_total
    rps = len(latencies_ms) / total_duration_sec

    print(f"\n================ BENCHMARK RESULTS ================")
    print(f"Total Packets Sent:       {NUM_PACKETS}")
    print(f"Successful Ingestions:    {len(latencies_ms)}")
    print(f"Failed / Errors:          {errors}")
    print(f"Total Elapsed Time:       {total_duration_sec:.2f} s")
    print(f"Throughput Rate:          {rps:.1f} packets/sec")
    if latencies_ms:
        print(f"Mean Ingest Latency:      {statistics.mean(latencies_ms):.2f} ms")
        print(f"p50 Ingest Latency:       {percentile(latencies_ms, .50):.2f} ms")
        print(f"p95 Ingest Latency:       {percentile(latencies_ms, .95):.2f} ms")
        print(f"p99 Ingest Latency:       {percentile(latencies_ms, .99):.2f} ms")
        print(f"Error Rate:               {(errors / NUM_PACKETS) * 100:.2f}%")
        print(f"Max Ingest Latency:       {max(latencies_ms):.2f} ms")
    print(f"===================================================\n")


if __name__ == "__main__":
    asyncio.run(run_stress_benchmark())
