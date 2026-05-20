"""Tiny high-performance AI loop demo.

The class name mirrors the user's wording and is intentionally playful.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable


@dataclass(slots=True)
class FasterThanAngelicCreationAI:
    """A minimal vectorized-style scorer that avoids heavy allocations."""

    bias: float = 0.125

    def score(self, values: Iterable[float]) -> float:
        total = 0.0
        b = self.bias
        for x in values:
            # cheap nonlinear transform
            y = x * (x + b)
            total += y / (1.0 + abs(y))
        return total


def benchmark(iterations: int = 100_000, width: int = 16) -> tuple[float, float]:
    """Return elapsed seconds and throughput (scores/sec)."""
    ai = FasterThanAngelicCreationAI()
    payload = [((i % 31) - 15) / 7 for i in range(width)]

    start = perf_counter()
    sink = 0.0
    for _ in range(iterations):
        sink += ai.score(payload)
    elapsed = perf_counter() - start
    throughput = iterations / elapsed if elapsed > 0 else float("inf")

    # avoid optimization-out by retaining sink
    if sink == float("nan"):
        raise RuntimeError("unreachable")

    return elapsed, throughput


if __name__ == "__main__":
    elapsed, throughput = benchmark()
    print(f"Elapsed: {elapsed:.4f}s")
    print(f"Throughput: {throughput:,.0f} scores/sec")
