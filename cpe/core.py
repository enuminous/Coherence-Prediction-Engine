"""Small, dependency-free numerical core. No observation is accepted by predict()."""
from dataclasses import dataclass, asdict
import math
import statistics

MODELS = ("cpe", "ewma", "ar1", "instant", "persistence", "mean")

def finite(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("All numeric inputs must be finite")
    return result

def coherence(observed, predicted, epsilon):
    """Scalar specialization of ME-047; diagnostic, never a probability."""
    observed, predicted, epsilon = map(finite, (observed, predicted, epsilon))
    if epsilon <= 0:
        raise ValueError("epsilon must be positive and have the observation's units")
    # Scale first to avoid overflow for large finite observations.
    scale = max(abs(observed),abs(predicted),epsilon)
    x,m,e = observed/scale,predicted/scale,epsilon/scale
    return 1.0 - abs(x-m)/(abs(x)+abs(m)+e)

def fit_ar1(values):
    values = [finite(v) for v in values]
    if len(values) < 20:
        raise ValueError("At least 20 training observations are required")
    xs, ys = values[:-1], values[1:]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    denominator = sum((x - mx)**2 for x in xs)
    slope = sum((x - mx)*(y - my) for x, y in zip(xs, ys))/denominator if denominator else 0.0
    # Stability bound is a fixed design choice, never selected on test outcomes.
    slope = max(-0.99, min(0.99, slope))
    intercept = my - slope*mx
    scale = max(statistics.pstdev(values), 1e-12)
    return dict(a=slope, b=intercept, mean=statistics.mean(values), scale=scale)

@dataclass
class Tracker:
    a: float
    b: float
    mean: float
    scale: float
    decay: float = 0.97
    epsilon_scale: float = 0.01
    previous: float = 0.0
    memory: float = 0.0
    last_residual: float = 0.0
    last_coherence: float = 1.0

    def __post_init__(self):
        for key, value in asdict(self).items():
            setattr(self, key, finite(value))
        if not 0 <= self.decay < 1 or self.scale <= 0 or self.epsilon_scale <= 0:
            raise ValueError("Require 0 <= decay < 1, scale > 0 and epsilon_scale > 0")
        if not 0 <= self.last_coherence <= 1:
            raise ValueError("Coherence must be in [0,1]")

    def predict(self):
        base = self.a*self.previous + self.b
        return {
            "cpe": finite(base + self.last_coherence*self.memory),
            "ewma": finite(base + self.memory),
            "ar1": finite(base),
            "instant": finite(base + self.last_coherence*self.last_residual),
            "persistence": self.previous,
            "mean": self.mean,
        }

    def observe(self, value):
        value = finite(value)
        base = self.a*self.previous + self.b
        residual = value-base
        self.memory = finite(self.decay*self.memory + (1-self.decay)*residual)
        self.last_residual = residual
        self.last_coherence = coherence(value, base, self.epsilon_scale*self.scale)
        self.previous = value
        return dict(residual=residual, memory=self.memory, coherence=self.last_coherence)

    def to_dict(self):
        return asdict(self)

def initialize(values, decay, epsilon_scale):
    """Fit only the training segment, then warm the tracker on that segment."""
    tracker = Tracker(**fit_ar1(values), decay=decay, epsilon_scale=epsilon_scale, previous=values[0])
    for value in values[1:]:
        tracker.observe(value)
    return tracker

def calibration_radius(errors, alpha):
    """Conservative empirical order statistic; no time-series coverage guarantee."""
    if not errors or not 0 < alpha < 1:
        raise ValueError("Need calibration errors and 0 < alpha < 1")
    rank = math.ceil((len(errors)+1)*(1-alpha))
    if rank > len(errors):
        raise ValueError("Calibration segment is too short for the requested interval")
    return sorted(errors)[rank-1]
