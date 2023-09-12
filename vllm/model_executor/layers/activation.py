"""Custom activation functions."""
import torch
import torch.nn as nn

from vllm import activation_ops

_ACTIVATION_REGISTRY = {
    "gelu": nn.GELU(),
    # NOTE: The following GELU functions may introduce small rounding errors.
    "gelu_new": nn.GELU(approximate="tanh"),
    "gelu_fast": nn.GELU(approximate="tanh"),
    "gelu_pytorch_tanh": nn.GELU(approximate="tanh"),
    "relu": nn.ReLU(),
}


def get_act_fn(act_fn: str) -> nn.Module:
    """Get an activation function by name."""
    act_fn = act_fn.lower()
    if act_fn in _ACTIVATION_REGISTRY:
        return _ACTIVATION_REGISTRY[act_fn]
    raise ValueError(f"Activation function {act_fn!r} is not supported.")


class SiluAndMul(nn.Module):
    """An activation function for SwiGLU.

    The function computes x -> silu(x[:d]) * x[d:] where d = x.shape[1] // 2.

    Shapes:
        x: (num_tokens, 2 * d)
        return: (num_tokens, d)
    """

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        num_tokens = x.shape[0]
        d = x.shape[1] // 2
        out = torch.empty(num_tokens, d, dtype=x.dtype, device=x.device)
        activation_ops.silu_and_mul(out, x)
        return out
