import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


"""Animated concept model: anti-parasitic AI agents in the bloodstream.

Red dots represent parasites, blue dots represent AI nanobots, and green dots are
neutralized parasites.
"""

rng = np.random.default_rng(7)

FIGSIZE = (9, 5)
X_MIN, X_MAX = 0, 100
Y_MIN, Y_MAX = 0, 60
N_PARASITES = 55
N_NANOBOTS = 12
DETECTION_RADIUS = 4.5
PARASITE_SPEED = 0.5
NANOBOT_SPEED = 1.5


parasites = rng.uniform([X_MIN, Y_MIN], [X_MAX, Y_MAX], size=(N_PARASITES, 2))
parasite_alive = np.ones(N_PARASITES, dtype=bool)
nanobots = rng.uniform([X_MIN, Y_MIN], [X_MAX, Y_MAX], size=(N_NANOBOTS, 2))


fig, ax = plt.subplots(figsize=FIGSIZE)
ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_title("Anti-parasitic AI Patrol in the Bloodstream")
ax.set_xlabel("Vessel position X")
ax.set_ylabel("Vessel position Y")
ax.set_facecolor("#101820")

parasite_scatter = ax.scatter([], [], c="#ff4d4d", s=32, label="Active parasites")
neutralized_scatter = ax.scatter([], [], c="#77dd77", s=28, label="Neutralized")
nanobot_scatter = ax.scatter([], [], c="#6ec6ff", s=75, marker="^", label="AI nanobots")
status_text = ax.text(0.02, 0.96, "", transform=ax.transAxes, color="white", va="top")
ax.legend(loc="lower right", facecolor="#1b2635", edgecolor="white", labelcolor="white")


flow = np.array([0.35, 0.0])


def step_positions():
    global parasites, nanobots

    # Parasites drift with blood flow + random motion.
    parasite_noise = rng.normal(0, PARASITE_SPEED, size=parasites.shape)
    parasites += flow + parasite_noise

    # Wrap around boundaries to keep everything in view.
    parasites[:, 0] = np.mod(parasites[:, 0] - X_MIN, X_MAX - X_MIN) + X_MIN
    parasites[:, 1] = np.mod(parasites[:, 1] - Y_MIN, Y_MAX - Y_MIN) + Y_MIN

    # Nanobots move toward nearest active parasite, otherwise patrol.
    for i in range(N_NANOBOTS):
        active_idx = np.where(parasite_alive)[0]
        if active_idx.size == 0:
            nanobots[i] += rng.normal(0, NANOBOT_SPEED * 0.2, size=2) + flow
            continue

        targets = parasites[active_idx]
        vectors = targets - nanobots[i]
        distances = np.linalg.norm(vectors, axis=1)
        nearest = np.argmin(distances)
        nearest_distance = distances[nearest]
        direction = vectors[nearest] / (nearest_distance + 1e-9)
        nanobots[i] += direction * NANOBOT_SPEED + flow * 0.5

    nanobots[:, 0] = np.clip(nanobots[:, 0], X_MIN, X_MAX)
    nanobots[:, 1] = np.clip(nanobots[:, 1], Y_MIN, Y_MAX)

    # Neutralize parasites within detection radius of any nanobot.
    active_idx = np.where(parasite_alive)[0]
    for idx in active_idx:
        dists = np.linalg.norm(nanobots - parasites[idx], axis=1)
        if np.any(dists <= DETECTION_RADIUS):
            parasite_alive[idx] = False


def update(_frame):
    step_positions()

    active = parasites[parasite_alive]
    neutralized = parasites[~parasite_alive]

    parasite_scatter.set_offsets(active if active.size else np.empty((0, 2)))
    neutralized_scatter.set_offsets(neutralized if neutralized.size else np.empty((0, 2)))
    nanobot_scatter.set_offsets(nanobots)

    status_text.set_text(
        f"Active: {active.shape[0]}   Neutralized: {neutralized.shape[0]}   "
        f"Coverage radius: {DETECTION_RADIUS:.1f}"
    )

    return parasite_scatter, neutralized_scatter, nanobot_scatter, status_text


ani = FuncAnimation(fig, update, frames=300, interval=80, blit=True)
plt.tight_layout()
plt.show()
