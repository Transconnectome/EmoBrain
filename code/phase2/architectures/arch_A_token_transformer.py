"""Architecture A (LLM-token style, simplified without LLM):
brain_emb + video_emb → project to common dim → [CLS, brain_tok, video_tok] sequence
→ 2-layer TransformerEncoder → CLS pooling → Linear → V/A

Trainable: brain_proj + video_proj + Transformer + CLS embedding + linear head.
"""
import torch
import torch.nn as nn


class TokenTransformer(nn.Module):
    def __init__(self, brain_dim: int, video_dim: int, n_out: int,
                 task_type: str = "binary",
                 d_model: int = 384, n_layers: int = 2, n_heads: int = 6,
                 dim_feedforward: int = 768, dropout: float = 0.1):
        super().__init__()
        self.task_type = task_type
        self.brain_proj = nn.Linear(brain_dim, d_model)
        self.video_proj = nn.Linear(video_dim, d_model)
        self.cls = nn.Parameter(torch.zeros(1, 1, d_model))
        nn.init.trunc_normal_(self.cls, std=0.02)
        self.type_emb = nn.Embedding(3, d_model)  # 0=CLS, 1=brain, 2=video
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=dim_feedforward,
            dropout=dropout, batch_first=True, activation="gelu",
        )
        self.transformer = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, n_out if task_type == "binary" else 1)

    def forward(self, brain, video):
        B = brain.shape[0]
        b_tok = self.brain_proj(brain).unsqueeze(1)  # (B, 1, d)
        v_tok = self.video_proj(video).unsqueeze(1)  # (B, 1, d)
        cls = self.cls.expand(B, -1, -1)             # (B, 1, d)
        x = torch.cat([cls, b_tok, v_tok], dim=1)    # (B, 3, d)
        type_ids = torch.tensor([0, 1, 2], device=x.device).unsqueeze(0).expand(B, -1)
        x = x + self.type_emb(type_ids)
        x = self.transformer(x)
        cls_out = self.norm(x[:, 0])
        return self.head(cls_out)
