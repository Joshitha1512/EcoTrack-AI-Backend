"""RecommendationAgent: Identifies highest contributors and generates prioritized recommendations"""

"""RecommendationAgent: Generates actionable recommendations"""

from typing import List, Dict
from schemas import Recommendation


class RecommendationAgent:
    """
    Agent responsible for generating personalized recommendations
    based on category-wise carbon emissions.
    """

    def generate(
        self,
        processed_data: Dict,
        emissions: Dict
    ) -> List[Recommendation]:
        """
        Generate top 3 recommendations based on highest emission categories.
        """

        recommendations: List[Recommendation] = []

        # Sort categories by emission (descending)
        sorted_categories = sorted(
            [
                ("transport", emissions["transport"]),
                ("electricity", emissions["electricity"]),
                ("diet", emissions["diet"]),
            ],
            key=lambda x: x[1],
            reverse=True
        )

        # Recommendation templates
        templates = {
            "transport": [
                ("Reduce car usage", "Use public transport, carpool, or walk when possible."),
                ("Limit flights", "Reduce air travel or choose lower-emission alternatives."),
            ],
            "electricity": [
                ("Reduce electricity usage", "Turn off unused appliances and use energy-efficient devices."),
                ("Switch to renewable energy", "Consider solar or green electricity providers."),
            ],
            "diet": [
                ("Reduce meat consumption", "Replace some meat meals with plant-based alternatives."),
                ("Choose local foods", "Eat locally sourced and seasonal foods to reduce emissions."),
            ],
        }

        # Generate recommendations from top categories
        for category, emission_value in sorted_categories:
            if category in templates:
                for title, desc in templates[category]:
                    recommendations.append(
                        Recommendation(
                            title=title,
                            description=desc,
                            potential_savings=round(emission_value * 0.15, 2),
                            category=category
                        )
                    )

        # Ensure exactly 3 recommendations
        return recommendations[:3]
