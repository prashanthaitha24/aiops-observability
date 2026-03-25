from __future__ import annotations

from .model_baselines import BASELINES, WEIGHTS


class AnomalyModel:
    def __init__(
        self,
        threshold: float,
        baselines: dict[str, float] | None = None,
        weights: dict[str, float] | None = None,
    ) -> None:
        self.threshold = threshold
        self.baselines = baselines or BASELINES
        self.weights = weights or WEIGHTS

    @staticmethod
    def _bounded_ratio(value: float, baseline: float) -> float:
        if baseline <= 0:
            return 0.0
        ratio = value / baseline
        if ratio <= 1.0:
            return 0.0
        score = (ratio - 1.0) / 2.0
        return max(0.0, min(score, 1.0))

    def score(self, features: dict[str, float]) -> dict[str, object]:
        weighted_score = 0.0
        reasons: list[str] = []
        component_scores: dict[str, float] = {}

        for feature_name, value in features.items():
            baseline = self.baselines.get(feature_name, 1.0)
            weight = self.weights.get(feature_name, 0.0)

            component_score = self._bounded_ratio(value, baseline)
            component_scores[feature_name] = component_score
            weighted_score += component_score * weight

            if component_score >= 0.30:
                reasons.append(
                    f"{feature_name} elevated "
                    f"(value={value:.2f}, baseline={baseline:.2f})"
                )

        final_score = max(0.0, min(weighted_score, 1.0))
        detected = final_score >= self.threshold

        return {
            "score": round(final_score, 4),
            "detected": detected,
            "reasons": reasons,
            "component_scores": component_scores,
        }
