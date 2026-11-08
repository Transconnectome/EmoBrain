"""34-dim output head (spec §6-6). z-space, NO activation, NO softmax.

The 34 Cowen-Keltner emotions co-occur (bittersweet = joy and sadness both high),
so any softmax / sum-to-1 / sigmoid destroys co-occurrence. Bare linear map to
raw z-space; the log1p_z preprocessing and per-emotion MSE live elsewhere.
"""

from __future__ import annotations

import torch.nn as nn


class Linear34(nn.Module):
    def __init__(self, hidden_dim: int, n_emotions: int = 34):
        super().__init__()
        self.fc = nn.Linear(hidden_dim, n_emotions)

    def forward(self, hidden):
        return self.fc(hidden)


class QueryReadoutHead(nn.Module):
    """LLM-native readout (B1). One SHARED scalar map applied to each of the 34
    emotion-query tokens. The prompt lists the 34 emotions and instructs a 0..1
    score per emotion; each query token (grounded in that emotion's name) attends
    to brain + video + caption inside the LLM, and its contextualised hidden
    state is projected to that emotion's score. Differentiation across emotions
    comes from the queries' distinct contextual states, not 34 separate heads, so
    the LLM's per-emotion semantics drive the output instead of a pooled probe.
    """

    def __init__(self, hidden_dim: int, n_emotions: int = 34):
        super().__init__()
        self.fc = nn.Linear(hidden_dim, 1)
        self.n_emotions = n_emotions

    def forward(self, query_states):        # (B, n_emotions, D) -> (B, n_emotions)
        return self.fc(query_states).squeeze(-1)
