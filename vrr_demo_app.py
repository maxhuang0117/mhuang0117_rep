import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="DP 2.1 VRR Demo", layout="wide")

st.title("DP 2.1 Adaptive-Sync (VRR) Demo")

st.markdown(
    """
This small demo illustrates how **Variable Refresh Rate (Adaptive-Sync)** in DP 2.1
differs from a **fixed refresh rate**, when the source content (e.g. a streamed/camera
video feed) is not perfectly periodic.
"""
)

mode = st.radio("Display mode", ["Fixed Refresh Rate", "DP 2.1 Adaptive-Sync (VRR)"], horizontal=True)

st.subheader("Content source timing")

JITTER_PRESETS = {
    "Native render (~0.5ms)": 0.5,
    "Local camera (~1ms)": 1,
    "Wired stream (~3ms)": 3,
    "Wireless stream (~6ms)": 6,
}

if "jitter_ms" not in st.session_state:
    st.session_state["jitter_ms"] = 6

preset_cols = st.columns(len(JITTER_PRESETS))
for col, (label, value) in zip(preset_cols, JITTER_PRESETS.items()):
    if col.button(label):
        st.session_state["jitter_ms"] = value

if mode == "Fixed Refresh Rate":
    col1, col2, col3 = st.columns(3)
    with col1:
        fixed_hz = st.slider("Fixed refresh rate (Hz)", 30, 120, 60, step=1)
    with col2:
        base_fps = st.slider("Avg content frame rate (fps)", 24, 90, 30, step=1)
    with col3:
        jitter_ms = st.slider("Frame timing jitter (+/- ms)", 0.0, 15.0, step=0.5, key="jitter_ms")
else:
    col1, col2 = st.columns(2)
    with col1:
        base_fps = st.slider("Avg content frame rate (fps)", 24, 90, 30, step=1)
    with col2:
        jitter_ms = st.slider("Frame timing jitter (+/- ms)", 0.0, 15.0, step=0.5, key="jitter_ms")

# Generate "content ready" timestamps with jitter over a 200ms window
duration_ms = 200
base_period = 1000.0 / base_fps
rng = np.random.default_rng(42)
content_ready = []
t = 0.0
while t < duration_ms:
    content_ready.append(t)
    jitter = rng.uniform(-jitter_ms, jitter_ms)
    t += max(2.0, base_period + jitter)
content_ready = np.array(content_ready)
content_ready = content_ready[content_ready <= duration_ms]

# Refresh timestamps
if mode == "Fixed Refresh Rate":
    fixed_period = 1000.0 / fixed_hz
    refresh_times = np.arange(0, duration_ms, fixed_period)
else:
    # VRR: refresh exactly when content is ready
    refresh_times = content_ready

# --- Plot ---
RED = "#d62728"
BLUE = "#1f77b4"
GRAY = "#888888"

fig, ax = plt.subplots(figsize=(11, 4))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

LANE_CONTENT = 1.0
LANE_REFRESH = 0.0


def draw_lane(times, y, color, label):
    # baseline
    ax.axhline(y, color="#dddddd", linewidth=1, zorder=1)
    # event markers (lollipops)
    ax.vlines(times, y, y + 0.18, color=color, linewidth=2, zorder=2)
    ax.plot(times, [y + 0.18] * len(times), "o", color=color, markersize=6,
            markeredgecolor="white", markeredgewidth=1, zorder=3, label=label)
    # interval arrows + labels below baseline
    for i in range(len(times) - 1):
        x0, x1 = times[i], times[i + 1]
        ax.annotate(
            "",
            xy=(x1, y - 0.06),
            xytext=(x0, y - 0.06),
            arrowprops=dict(arrowstyle="<->", color=color, lw=1, alpha=0.6),
            zorder=2,
        )
        ax.text(
            (x0 + x1) / 2,
            y - 0.13,
            f"{x1 - x0:.1f}",
            ha="center",
            va="top",
            fontsize=8,
            color=color,
        )


draw_lane(content_ready, LANE_CONTENT, RED, "Content frame ready")
draw_lane(refresh_times, LANE_REFRESH, BLUE, "Display refresh")

ax.set_xlim(0, duration_ms)
ax.set_ylim(-0.35, 1.35)
ax.set_yticks([LANE_REFRESH, LANE_CONTENT])
ax.set_yticklabels(["Display\nrefresh", "Content\nframe ready"], fontsize=10)

ax.set_xticks(np.arange(0, duration_ms + 1, 20))
ax.set_xticks(np.arange(0, duration_ms + 1, 5), minor=True)
ax.grid(axis="x", which="major", color="#cfcfcf", linewidth=0.8, zorder=0)
ax.grid(axis="x", which="minor", color="#ebebeb", linewidth=0.5, zorder=0)

ax.tick_params(axis="x", which="major", labelsize=10)
ax.tick_params(axis="y", which="both", length=0)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#bbbbbb")

ax.set_xlabel("Time (ms)   —   major grid 20 ms/div, minor grid 5 ms/div", fontsize=10, labelpad=10)
ax.set_title(mode, fontsize=14, fontweight="bold", pad=14)

fig.tight_layout()
st.pyplot(fig)

# --- Vblank / Vtotal chart ---
st.subheader("Per-frame Vblank duration")

st.markdown(
    "Adaptive-Sync keeps **pixel clock** and **Htotal** fixed, and varies **Vtotal** by "
    "stretching/shrinking **Vblank** so each frame's duration matches the refresh interval above."
)

vcol1, vcol2, vcol3 = st.columns(3)
with vcol1:
    pclk_mhz = st.number_input("Pixel clock (MHz)", value=148.5, step=0.5)
with vcol2:
    htotal = st.number_input("Htotal (pixels)", value=2200, step=10)
with vcol3:
    vactive = st.number_input("Vactive (lines)", value=1080, step=10)

frame_intervals_ms = np.diff(refresh_times)
line_time_us = htotal / pclk_mhz  # time for one line, in microseconds
vtotal_lines = (frame_intervals_ms * 1000.0) / line_time_us
vblank_lines = vtotal_lines - vactive

fig2, ax2 = plt.subplots(figsize=(11, 3))
fig2.patch.set_facecolor("white")
ax2.set_facecolor("white")

x_pos = np.arange(len(vblank_lines))
bar_color = BLUE if mode != "Fixed Refresh Rate" else GRAY
ax2.bar(x_pos, vblank_lines, color=bar_color, width=0.6, zorder=2)
ax2.axhline(vblank_lines[0] if len(vblank_lines) else 0, color="#cccccc", linewidth=1, zorder=1, linestyle="--")

for x, v in zip(x_pos, vblank_lines):
    ax2.text(x, v + max(vblank_lines) * 0.02, f"{v:.0f}", ha="center", va="bottom", fontsize=8, color="#444444")

ax2.set_xticks(x_pos)
ax2.set_xticklabels([f"F{i+1}" for i in x_pos], fontsize=9)
ax2.set_ylabel("Vblank (lines)", fontsize=10)
ax2.set_title("Vblank lines added per frame to match refresh timing", fontsize=12, pad=10)

for spine in ["top", "right"]:
    ax2.spines[spine].set_visible(False)
ax2.spines["left"].set_color("#bbbbbb")
ax2.spines["bottom"].set_color("#bbbbbb")
ax2.grid(axis="y", color="#ebebeb", linewidth=0.7, zorder=0)

fig2.tight_layout()
st.pyplot(fig2)

with st.expander("Show per-frame calculation breakdown"):
    st.markdown(f"**Line time** = Htotal / pclk = {htotal} / {pclk_mhz} MHz = **{line_time_us:.3f} µs/line**")
    rows = []
    for i, (interval, vt, vb) in enumerate(zip(frame_intervals_ms, vtotal_lines, vblank_lines), start=1):
        rows.append(
            {
                "Frame": f"F{i}",
                "Interval (ms)": f"{interval:.2f}",
                "Vtotal = interval(µs) / line_time": f"{interval*1000:.1f} / {line_time_us:.3f} = {vt:.1f}",
                "Vblank = Vtotal - Vactive": f"{vt:.1f} - {vactive} = {vb:.1f}",
            }
        )
    st.table(rows)

if mode == "Fixed Refresh Rate":
    st.caption(
        "Fixed refresh rate → Vtotal/Vblank is constant every frame, regardless of when "
        "content is actually ready (dashed line = constant Vblank)."
    )
else:
    st.caption(
        "Adaptive-Sync → Vblank stretches or shrinks each frame so Vtotal lines up the "
        "refresh exactly with content readiness (dashed line = baseline Vblank for the first frame)."
    )

# --- Stats ---
st.subheader("Stats")

if mode == "Fixed Refresh Rate":
    # For each content frame, find how long it waits until next refresh
    waits = []
    for c in content_ready:
        next_refresh = refresh_times[refresh_times >= c]
        if len(next_refresh) > 0:
            waits.append(next_refresh[0] - c)
    waits = np.array(waits)
    st.metric("Avg wait for next refresh (ms)", f"{waits.mean():.2f}")
    st.metric("Max wait / stutter risk (ms)", f"{waits.max():.2f}")
    st.caption(
        "With a fixed refresh rate, frames that miss the refresh window must wait "
        "until the next tick, causing variable latency, judder, or tearing."
    )
else:
    intervals = np.diff(refresh_times)
    st.metric("Min refresh interval (ms)", f"{intervals.min():.2f}")
    st.metric("Max refresh interval (ms)", f"{intervals.max():.2f}")
    st.caption(
        "With VRR, the panel refreshes exactly when each frame is ready, so latency "
        "between content generation and display is minimized regardless of jitter."
    )

st.markdown("---")
st.markdown(
    """
**Notes for integration into the main app:**
- This models a single video stream's frame cadence vs. display refresh.
- For DP 2.1, VRR range is communicated via DPCD registers (min/max refresh Hz the panel supports).
- A future tab could take the existing eDP/DSI per-stream PCLK tables and add a
  "VRR range" column (min/max PCLK) instead of a single required PCLK value.
"""
)
