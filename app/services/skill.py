from trueskill import TrueSkill, Rating
from app.config import settings

def make_ts_env() -> TrueSkill:
    return TrueSkill(
        mu=settings.ts_mu,
        sigma=settings.ts_sigma,
        beta=settings.ts_beta,
        tau=settings.ts_tau,
        draw_probability=settings.ts_draw_prob,
    )

def skill(mu: float, sigma: float, *, teamer: bool = False) -> float:
    base = mu - max(sigma - settings.ts_sigma_free, 0.0)
    if teamer:
        base += settings.ts_teamer_boost * (mu - settings.ts_mu)
    return base

def skill_from_rating(r: Rating, *, teamer: bool = False) -> float:
    return skill(r.mu, r.sigma, teamer=teamer)