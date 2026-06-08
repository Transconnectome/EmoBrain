"""
Probe heads vendored from SwiFT_v2 downstream_optuna pipeline.

Source: /pscratch/sd/s/sjmoon/SwiFT_v2/downstream_optuna/models.py (class `mlp`)
Vendored so FEELIN probes use the identical head used by SwiFT's downstream
benchmarking (no head-architecture confound when comparing).

Requires: monai (MLPBlock, trunc_normal_).
"""
import torch
import torch.nn as nn
from monai.networks.blocks import MLPBlock as Mlp
from monai.networks.layers import trunc_normal_


class SwiftMLP(nn.Module):
    """
    SwiFT_v2 downstream MLP head (identical to downstream_optuna/models.py:mlp).

    Default config matches SwiFT pipeline:
      num_blocks=2, mlp_ratio=4.0, dim-preserving residual MLPBlock + LayerNorm.

    Use already_pooled=True when input is (B, C) embedding (FEELIN case).
    """

    def __init__(self,
                 num_classes=2,
                 num_blocks=2,
                 hidden_dim=96,
                 norm_layer=nn.LayerNorm,
                 mlp_ratio=4.0,
                 drop_rate=0.0,
                 post_avg_pool=False,
                 already_pooled=False):
        super().__init__()
        self.num_classes = num_classes
        self.already_pooled = already_pooled
        self.post_avg_pool = post_avg_pool
        self.num_blocks = num_blocks

        self.blks = nn.ModuleList()
        for _ in range(num_blocks):
            layer = nn.Sequential(
                Mlp(hidden_size=hidden_dim, mlp_dim=int(hidden_dim * mlp_ratio),
                    dropout_rate=drop_rate),
                norm_layer(hidden_dim),
            )
            self.blks.append(layer)

        self.head = nn.Linear(hidden_dim, num_classes)
        self.avgpool = nn.AdaptiveAvgPool1d(1)

        self.init_weights()

    def init_weights(self):
        def _init(m):
            if isinstance(m, nn.Linear):
                trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.LayerNorm):
                nn.init.constant_(m.bias, 0)
                nn.init.constant_(m.weight, 1.0)
        self.apply(_init)

    def forward(self, x, return_probs=False):
        if x.dim() == 6:
            x = x.flatten(start_dim=2).transpose(1, 2)

        if self.already_pooled:
            if x.dim() == 3:
                x = x.squeeze(-1)
            for blk in self.blks:
                x = blk(x)
        elif self.post_avg_pool:
            for blk in self.blks:
                x = blk(x)
            x = self.avgpool(x.transpose(1, 2)).squeeze(-1)
        else:
            x = self.avgpool(x.transpose(1, 2)).squeeze(-1)
            for blk in self.blks:
                x = blk(x)

        embedding = x
        logits = self.head(x)
        if return_probs:
            probs = torch.softmax(logits, dim=1)
            return embedding, probs
        return logits


class SmallMLP(nn.Module):
    """
    Smaller probe head for small-N regime (sub-01 ~900 train samples).
    Projects in_dim -> hidden, then 2 MLPBlocks at hidden dim.

    Default: hidden=256, mlp_ratio=2.0, drop=0.5  ->  ~0.4M params
    (vs SwiftMLP at hidden=768, ratio=4.0, drop=0.3 -> 9.4M params)
    """

    def __init__(self, in_dim, num_classes=2, hidden=256, num_blocks=2,
                 mlp_ratio=2.0, drop_rate=0.5, norm_layer=nn.LayerNorm):
        super().__init__()
        self.proj = nn.Linear(in_dim, hidden)
        self.proj_norm = norm_layer(hidden)
        self.blks = nn.ModuleList()
        for _ in range(num_blocks):
            layer = nn.Sequential(
                Mlp(hidden_size=hidden, mlp_dim=int(hidden * mlp_ratio),
                    dropout_rate=drop_rate),
                norm_layer(hidden),
            )
            self.blks.append(layer)
        self.head = nn.Linear(hidden, num_classes)
        self.init_weights()

    def init_weights(self):
        def _init(m):
            if isinstance(m, nn.Linear):
                trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.LayerNorm):
                nn.init.constant_(m.bias, 0)
                nn.init.constant_(m.weight, 1.0)
        self.apply(_init)

    def forward(self, x):
        x = self.proj_norm(self.proj(x))
        for blk in self.blks:
            x = blk(x)
        return self.head(x)
