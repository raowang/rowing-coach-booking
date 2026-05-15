"""
Performance Tests for Rowing Coach Booking - Concurrent Booking Scenarios

Tests concurrent booking scenarios to ensure the system handles
high-load situations correctly.

Run with: pytest tests/test_performance.py -v
"""

import asyncio
import time
from collections import Counter
from datetime import datetime, timedelta
from typing import List

import httpx
import pytest


BASE_URL = "http://localhost:8000"
TEST_COACH_ID = "test-coach-001"
TEST_MEMBER_BASE = "test-member-"


class BookingRequest:
    def __init__(self, member_id: str, coach_id: str, scheduled_time: str):
        self.member_id = member_id
        self.coach_id = coach_id
        self.scheduled_time = scheduled_time

    def to_dict(self):
        return {
            "openid": self.member_id,
            "coach_id": self.coach_id,
            "scheduled_time": self.scheduled_time,
        }


async def create_booking(client: httpx.AsyncClient, request: BookingRequest) -> dict:
    """Create a booking and return the result."""
    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/bookings",
            json=request.to_dict(),
            timeout=30.0,
        )
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code < 500 else None,
            "error": None,
        }
    except Exception as e:
        return {"status_code": 0, "data": None, "error": str(e)}


@pytest.mark.asyncio
async def test_concurrent_booking_same_timeslot():
    """
    Test: Multiple members trying to book the same timeslot simultaneously.

    Expected: Only ONE booking succeeds, others should get conflict error.
    """
    print("\n=== Test: Concurrent Booking Same Timeslot ===")

    timeslot = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 09:00")

    num_concurrent = 10
    requests = [
        BookingRequest(
            member_id=f"{TEST_MEMBER_BASE}{i}",
            coach_id=TEST_COACH_ID,
            scheduled_time=timeslot,
        )
        for i in range(num_concurrent)
    ]

    async with httpx.AsyncClient() as client:
        start_time = time.time()
        results = await asyncio.gather(
            *[create_booking(client, req) for req in requests]
        )
        elapsed = time.time() - start_time

    success_count = sum(1 for r in results if r["status_code"] == 201)
    conflict_count = sum(
        1
        for r in results
        if r["status_code"] == 409
        or (r["data"] and "conflict" in str(r["data"]).lower())
    )
    error_count = sum(1 for r in results if r["status_code"] == 0)

    print(f"  Concurrent requests: {num_concurrent}")
    print(f"  Successful bookings: {success_count}")
    print(f"  Conflict rejections: {conflict_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Throughput: {num_concurrent / elapsed:.2f} req/s")

    assert success_count == 1, f"Expected 1 success, got {success_count}"
    assert conflict_count == num_concurrent - 1, (
        f"Expected {num_concurrent - 1} conflicts, got {conflict_count}"
    )


@pytest.mark.asyncio
async def test_booking_throughput():
    """
    Test: Measure booking throughput under load.

    Creates bookings for different timeslots to avoid conflicts.
    """
    print("\n=== Test: Booking Throughput ===")

    num_requests = 100
    base_time = datetime.now() + timedelta(days=7)

    requests = [
        BookingRequest(
            member_id=f"{TEST_MEMBER_BASE}perf-{i}",
            coach_id=TEST_COACH_ID,
            scheduled_time=(base_time + timedelta(minutes=i * 30)).strftime(
                "%Y-%m-%d %H:%M"
            ),
        )
        for i in range(num_requests)
    ]

    async with httpx.AsyncClient() as client:
        start_time = time.time()
        results = await asyncio.gather(
            *[create_booking(client, req) for req in requests]
        )
        elapsed = time.time() - start_time

    success_count = sum(1 for r in results if r["status_code"] == 201)
    error_count = sum(1 for r in results if r["status_code"] not in [200, 201])

    print(f"  Total requests: {num_requests}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Throughput: {num_requests / elapsed:.2f} req/s")

    assert success_count == num_requests, f"Expected all {num_requests} to succeed"


@pytest.mark.asyncio
async def test_booking_latency():
    """
    Test: Measure booking API latency.

    Target: p95 < 500ms under normal load.
    """
    print("\n=== Test: Booking Latency ===")

    num_requests = 50
    base_time = datetime.now() + timedelta(days=14)

    latencies = []

    async with httpx.AsyncClient() as client:
        for i in range(num_requests):
            request = BookingRequest(
                member_id=f"{TEST_MEMBER_BASE}lat-{i}",
                coach_id=TEST_COACH_ID,
                scheduled_time=(base_time + timedelta(minutes=i)).strftime(
                    "%Y-%m-%d %H:%M"
                ),
            )

            start = time.time()
            await create_booking(client, request)
            latency = (time.time() - start) * 1000
            latencies.append(latency)

    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    avg = sum(latencies) / len(latencies)

    print(f"  Requests: {num_requests}")
    print(f"  Average latency: {avg:.2f}ms")
    print(f"  P50 latency: {p50:.2f}ms")
    print(f"  P95 latency: {p95:.2f}ms")
    print(f"  P99 latency: {p99:.2f}ms")

    assert p95 < 500, f"P95 latency {p95:.2f}ms exceeds 500ms target"


@pytest.mark.asyncio
async def test_concurrent_read_write():
    """
    Test: Mixed read/write operations under concurrent load.

    Simulates real-world scenario with members browsing coaches
    while others are making bookings.
    """
    print("\n=== Test: Concurrent Read/Write ===")

    async def read_coaches(client: httpx.AsyncClient) -> dict:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/coaches", timeout=10.0)
            return {"status": "success", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def read_schedules(client: httpx.AsyncClient) -> dict:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/schedules/available",
                params={"coach_id": TEST_COACH_ID, "date": "2025-12-25"},
                timeout=10.0,
            )
            return {"status": "success", "status_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    num_operations = 100
    read_ratio = 0.7

    operations = []
    for i in range(num_operations):
        if i % 10 < 7:
            operations.append(("read", i))
        else:
            operations.append(("write", i))

    async with httpx.AsyncClient() as client:
        tasks = []
        for op_type, idx in operations:
            if op_type == "read":
                if idx % 2 == 0:
                    tasks.append(read_coaches(client))
                else:
                    tasks.append(read_schedules(client))
            else:
                request = BookingRequest(
                    member_id=f"{TEST_MEMBER_BASE}rw-{idx}",
                    coach_id=TEST_COACH_ID,
                    scheduled_time=(
                        datetime.now() + timedelta(days=21, minutes=idx)
                    ).strftime("%Y-%m-%d %H:%M"),
                )
                tasks.append(create_booking(client, request))

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

    read_results = [r for r in results[: int(num_operations * read_ratio)] if isinstance(r, dict)]
    write_results = [r for r in results[int(num_operations * read_ratio) :] if isinstance(r, dict)]

    read_success = sum(1 for r in read_results if r.get("status") == "success")
    write_success = sum(1 for r in write_results if r.get("status_code") == 201)

    print(f"  Total operations: {num_operations}")
    print(f"  Read operations: {len(read_results)}, success: {read_success}")
    print(f"  Write operations: {len(write_results)}, success: {write_success}")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Throughput: {num_operations / elapsed:.2f} ops/s")

    assert read_success > 0, "Read operations should succeed"
    assert write_success > 0, "Write operations should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])