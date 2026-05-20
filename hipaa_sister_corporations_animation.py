"""
Animated network plot: "HIPAA and its sister corporations"

This script builds a simple animated relationship graph using matplotlib.
Run:
    python hipaa_sister_corporations_animation.py
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Central entity and sister corporations (example structure)
NODES = [
    "HIPAA",
    "HealthData Systems",
    "CareCloud Partners",
    "SecureClaims Inc.",
    "MediAudit Group",
    "PatientFlow Labs",
]

# Edges from HIPAA to each sister corporation
EDGES = [("HIPAA", node) for node in NODES[1:]]

# Colors for visual distinction
NODE_COLORS = {
    "HIPAA": "#2563eb",
    "HealthData Systems": "#16a34a",
    "CareCloud Partners": "#f59e0b",
    "SecureClaims Inc.": "#ef4444",
    "MediAudit Group": "#9333ea",
    "PatientFlow Labs": "#0ea5e9",
}


def circular_layout(nodes: list[str], radius: float = 3.0) -> dict[str, tuple[float, float]]:
    """Place HIPAA in center and sisters around a circle."""
    positions: dict[str, tuple[float, float]] = {nodes[0]: (0.0, 0.0)}
    angle_step = 2 * np.pi / (len(nodes) - 1)

    for i, node in enumerate(nodes[1:]):
        angle = i * angle_step
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        positions[node] = (x, y)

    return positions


def build_animation() -> FuncAnimation:
    positions = circular_layout(NODES)

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_facecolor("#0f172a")
    fig.patch.set_facecolor("#0f172a")
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-4.5, 4.5)
    ax.axis("off")

    # Draw static labels and nodes
    for node in NODES:
        x, y = positions[node]
        size = 2000 if node == "HIPAA" else 1300
        ax.scatter(
            x,
            y,
            s=size,
            c=NODE_COLORS[node],
            alpha=0.92,
            edgecolors="#e2e8f0",
            linewidths=2,
            zorder=3,
        )
        ax.text(
            x,
            y,
            node,
            color="white",
            fontsize=11,
            ha="center",
            va="center",
            weight="bold",
            zorder=4,
        )

    ax.set_title(
        "HIPAA and Sister Corporations\nAnimated Relationship Network",
        color="white",
        fontsize=16,
        weight="bold",
        pad=16,
    )

    # Pre-create line artists for edge animation
    lines = []
    for start, end in EDGES:
        x0, y0 = positions[start]
        x1, y1 = positions[end]
        (line,) = ax.plot([x0, x0], [y0, y0], color="#93c5fd", linewidth=2.8, alpha=0.85, zorder=2)
        lines.append((line, x0, y0, x1, y1))

    pulse = ax.scatter([0], [0], s=2300, c="#60a5fa", alpha=0.08, zorder=1)

    total_frames = 180

    def update(frame: int):
        progress = min(1.0, frame / 70)

        for idx, (line, x0, y0, x1, y1) in enumerate(lines):
            edge_progress = np.clip((frame - idx * 8) / 55, 0.0, 1.0)
            xn = x0 + (x1 - x0) * edge_progress
            yn = y0 + (y1 - y0) * edge_progress
            line.set_data([x0, xn], [y0, yn])

        pulse_size = 2300 + 1100 * (0.5 + 0.5 * np.sin(frame * 0.18)) * progress
        pulse_alpha = 0.05 + 0.07 * (0.5 + 0.5 * np.sin(frame * 0.18))
        pulse.set_sizes([pulse_size])
        pulse.set_alpha(float(pulse_alpha))

        return [line for line, *_ in lines] + [pulse]

    animation = FuncAnimation(fig, update, frames=total_frames, interval=40, blit=True, repeat=True)
    plt.tight_layout()
    return animation


if __name__ == "__main__":
    anim = build_animation()
    plt.show()
