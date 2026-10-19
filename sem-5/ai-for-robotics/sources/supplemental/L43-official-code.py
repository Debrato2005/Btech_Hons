import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import torch
import torch.nn as nn
import torch.optim as optim
from IPython.display import HTML

SEED = 0
np.random.seed(SEED)
torch.manual_seed(SEED)


ROWS, COLS = 4, 5
# Note that these co-ordinates are considered as (y,x)
START = (0, 0)
GOAL = (3, 4)
WALLS = {(0, 1), (2, 3), (3,0)}   # one obstacle — try moving it or adding more!

ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]      # up, down, left, right
ACTION_NAMES = ["UP", "DOWN", "LEFT", "RIGHT"]

def is_free(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS and (r, c) not in WALLS

def show_maze(ax, robot_pos=None):
    grid = np.zeros((ROWS, COLS))
    for (wr, wc) in WALLS:
        grid[wr, wc] = 1
    ax.imshow(grid, cmap=ListedColormap(["white", "#2b2b2b"]), vmin=0, vmax=1)
    ax.scatter(START[1], START[0], c="tab:green", s=180, marker="o", zorder=3, label="Start")
    ax.scatter(GOAL[1], GOAL[0], c="tab:red", s=220, marker="*", zorder=3, label="Goal")
    if robot_pos is not None:
        ax.scatter(robot_pos[1], robot_pos[0], c="tab:blue", s=220, marker="o", zorder=4)

    # Set major ticks for cell labels (0, 1, 2, ...)
    ax.set_xticks(np.arange(COLS))
    ax.set_yticks(np.arange(ROWS))

    # Set minor ticks for grid lines *between* cells
    ax.set_xticks(np.arange(-0.5, COLS, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, ROWS, 1), minor=True)

    # Draw grid lines on minor ticks
    ax.grid(which='minor', color="lightgray", linestyle='-', linewidth=0.5)
    # Hide major grid lines (which would otherwise appear in the middle of cells)
    ax.grid(which='major', color='white', linestyle='-', linewidth=0)

    # Ensure cells are square
    ax.set_aspect('equal')

fig, ax = plt.subplots(figsize=(4.5, 3.5))
show_maze(ax)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=2, frameon=False)
ax.set_title("The maze")
plt.show()

def manhattan(r, c):
    return abs(r - GOAL[0]) + abs(c - GOAL[1])

def wall_sensor(r, c):
    """1 if that neighbor is a wall / off-grid, else 0 — one bit per direction."""
    bits = []
    for dr, dc in ACTIONS:
        nr, nc = r + dr, c + dc
        bits.append(0.0 if is_free(nr, nc) else 1.0)
    return bits

def featurize(r, c):
    return np.array([r / ROWS, c / COLS] + wall_sensor(r, c), dtype=np.float32)

# preference order used only to break ties among equally-good directions
PREFERENCE = [3, 1, 2, 0]  # RIGHT, DOWN, LEFT, UP

def best_direction(r, c):
    cur_d = manhattan(r, c)
    for ai in PREFERENCE:                       # prefer moves that get closer
        dr, dc = ACTIONS[ai]
        nr, nc = r + dr, c + dc
        if is_free(nr, nc) and manhattan(nr, nc) < cur_d:
            return ai
    for ai in PREFERENCE:                       # fallback: any move that doesn't get worse
        dr, dc = ACTIONS[ai]
        nr, nc = r + dr, c + dc
        if is_free(nr, nc) and manhattan(nr, nc) <= cur_d:
            return ai
    return None

X, y = [], []
cells_for_training = [] # Store cell coordinates to pair with X and y
for r in range(ROWS):
    for c in range(COLS):
        if is_free(r, c) and (r, c) != GOAL:
            a = best_direction(r, c)
            X.append(featurize(r, c))
            y.append(a)
            cells_for_training.append((r, c))

X = np.stack(X)
y = np.array(y)
print(f"Training samples: {X.shape[0]}  |  feature size: {X.shape[1]}")

# Modified print statement to include the feature vector and the one-hot target
for i, (feat_vec, action_idx, (r, c)) in enumerate(zip(X, y, cells_for_training)):
    target_output = np.zeros(len(ACTIONS), dtype=np.int32)
    target_output[action_idx] = 1
    print(f"  cell {(r, c)} (features: {feat_vec})  ->  Target Output: {target_output} ({ACTION_NAMES[action_idx]}) ")

class NavNet(nn.Module):
    def __init__(self, in_dim=6, hidden=16, out_dim=4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.net(x)

X_t = torch.from_numpy(X)
y_t = torch.from_numpy(y).long()

model = NavNet()
optimizer = optim.Adam(model.parameters(), lr=0.05)
loss_fn = nn.CrossEntropyLoss()

EPOCHS = 60
loss_history = []
for epoch in range(EPOCHS):
    optimizer.zero_grad()
    logits = model(X_t)
    loss = loss_fn(logits, y_t)
    loss.backward()
    optimizer.step()
    loss_history.append(loss.item())

with torch.no_grad():
    train_acc = (model(X_t).argmax(dim=1) == y_t).float().mean().item()
print(f"Final loss: {loss_history[-1]:.4f}   |   accuracy: {train_acc*100:.0f}%")


@torch.no_grad()
def navigate(model, max_steps=10):
    r, c = START
    path = [(r, c)]
    for _ in range(max_steps):
        if (r, c) == GOAL:
            break
        feat = torch.from_numpy(featurize(r, c)).unsqueeze(0)
        scores = model(feat).squeeze(0).numpy()
        valid = [ai for ai, (dr, dc) in enumerate(ACTIONS) if is_free(r + dr, c + dc)]
        chosen = max(valid, key=lambda ai: scores[ai])
        dr, dc = ACTIONS[chosen]
        r, c = r + dr, c + dc
        path.append((r, c))
    return path

path = navigate(model)
print("Robot's path:", path)
print("Steps taken:", len(path) - 1)


TRAIN_FRAMES = 30                                  # how many points of the loss curve to reveal
sample_idx = np.linspace(0, EPOCHS - 1, TRAIN_FRAMES).astype(int)
sampled_losses = [loss_history[i] for i in sample_idx]

DRIVE_FRAMES = len(path)                           # one frame per step, including the start
TOTAL_FRAMES = TRAIN_FRAMES + DRIVE_FRAMES

fig, (ax_loss, ax_maze) = plt.subplots(1, 2, figsize=(10, 4))

# --- left panel: loss curve ---
ax_loss.set_xlim(0, EPOCHS)
ax_loss.set_ylim(0, max(loss_history) * 1.1)
ax_loss.set_xlabel("Training step")
ax_loss.set_ylabel("Loss")
ax_loss.set_title("Neural network updating")
ax_loss.grid(True)
loss_line, = ax_loss.plot([], [], color="tab:purple", linewidth=2)

# --- right panel: maze ---
show_maze(ax_maze, robot_pos=START)
ax_maze.set_title("Training...")

def init():
    loss_line.set_data([], [])
    return (loss_line,)

def update(frame):
    if frame < TRAIN_FRAMES:
        xs = sample_idx[:frame + 1]
        ys = sampled_losses[:frame + 1]
        loss_line.set_data(xs, ys)
        ax_maze.set_title("Training...")
    else:
        loss_line.set_data(sample_idx, sampled_losses)     # keep full curve visible
        step = frame - TRAIN_FRAMES
        ax_maze.clear()
        show_maze(ax_maze, robot_pos=path[step])
        if step > 0:
            rows = [p[0] for p in path[:step + 1]]
            cols = [p[1] for p in path[:step + 1]]
            ax_maze.plot(cols, rows, color="tab:blue", linewidth=2, alpha=0.5, zorder=2)
        ax_maze.set_title(f"Driving — step {step} / {len(path) - 1}")
    return (loss_line,)

anim = animation.FuncAnimation(
    fig, update, frames=TOTAL_FRAMES, init_func=init, interval=200, blit=False
)
plt.close(fig)
HTML(anim.to_jshtml())
