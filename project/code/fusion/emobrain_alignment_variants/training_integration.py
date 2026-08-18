"""Minimal trainer integration for the EmoBrain alignment model variants.

Use this helper immediately after your ordinary supervised task loss is computed.

DDP-safe:
    loss = add_alignment_aux_loss(model, loss)

Then call:
    optimizer.zero_grad(...)
    loss.backward()
    optimizer.step()

Variant-specific forward recommendations
----------------------------------------

RASA:
    pred = model(fmri, video=video, caption=caption)

SGAR (ground-truth target strongly recommended):
    pred = model(
        fmri,
        video=video,
        caption=caption,
        target_z=target_z,
    )

Consensus (exact IDs strongly recommended):
    pred = model(
        fmri,
        video=video,
        caption=caption,
        clip_id=clip_id,
        subject_id=subject_id,
    )

The original brain-only/student forward remains:
    pred = model(fmri)

For logging:
    core = unwrap_model(model)
    print(core.last_aux_losses)
    print(core.last_aux_metrics)
"""


def unwrap_model(model):
    """Return underlying nn.Module for DDP/DataParallel or the model itself."""
    return model.module if hasattr(model, "module") else model


def add_alignment_aux_loss(model, base_loss):
    """Add variant-specific auxiliary objective without changing criterion code."""
    core = unwrap_model(model)
    fn = getattr(core, "loss_with_aux", None)
    return fn(base_loss) if fn is not None else base_loss
