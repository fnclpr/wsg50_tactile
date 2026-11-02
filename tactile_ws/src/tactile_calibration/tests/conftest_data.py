import numpy as np


def synthetic(n=1500, seed=0, noise=0.01):
    """25 debiased voltages -> 6 wrench components (smooth nonlinear map)."""
    rng = np.random.default_rng(seed)
    latent = rng.uniform(0.0, 1.0, size=(n, 4))
    mix = rng.normal(size=(4, 25))
    v = latent @ mix * 0.5 + noise * rng.normal(size=(n, 25))
    y = np.stack([
        2.0 * latent[:, 0] - latent[:, 1],
        latent[:, 2] ** 2,
        -5.0 * latent[:, 3] + 0.5 * latent[:, 0],
        0.01 * np.tanh(latent[:, 1] * 3.0),
        np.zeros(n),                       # constant column on purpose
        0.02 * (latent[:, 0] - latent[:, 2]),
    ], axis=1)
    return v, y
