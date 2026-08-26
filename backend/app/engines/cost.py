from typing import Dict, Any, Tuple

class CostEngine:
    @staticmethod
    def evaluate_cost_risk(
        parameters: Dict[str, Any],
        expected_cost: float = 0.10
    ) -> Tuple[float, float, float, float]:
        """
        Evaluates cost risk based on parameters (tokens, amounts, agent loops).
        Returns: (cost_risk, estimated_cost, expected_cost, deviation)
        """
        tokens = parameters.get("estimated_tokens", 1000)
        loops = parameters.get("agent_loops", 1)
        
        # Calculate estimated cost
        estimated_cost = (tokens / 1000.0) * 0.02 * loops
        if estimated_cost <= 0:
            estimated_cost = expected_cost

        deviation = estimated_cost / max(0.01, expected_cost)

        if deviation <= 1.0:
            cost_risk = 0.0
        else:
            cost_risk = min(1.0, max(0.0, (deviation - 1.0) / 3.0))

        return cost_risk, estimated_cost, expected_cost, deviation
