"""SupervisorAgent: Controls execution order and passes outputs between agents"""

from typing import Dict, Any, Optional, List

from agents.input_agent import InputAgent
from agents.carbon_agent import CarbonEstimationAgent
from agents.recommendation_agent import RecommendationAgent
from agents.explanation_agent import ExplanationAgent

from schemas import AnalyzeRequest, AnalyzeResponse, Recommendation
from supabase_client import get_supabase_client


class SupervisorAgent:
    def __init__(self):
        self.input_agent = InputAgent()
        self.carbon_agent = CarbonEstimationAgent()
        self.recommendation_agent = RecommendationAgent()
        self.explanation_agent = ExplanationAgent()

    # ----------------------------
    # Fetch previous analysis
    # ----------------------------
    def _get_previous_total(
        self,
        user_id: Optional[str],
        access_token: Optional[str]
    ) -> Optional[float]:

        if not user_id or not access_token:
            return None

        try:
            supabase = get_supabase_client(access_token)

            result = (
                supabase
                .table("eco_analysis")
                .select("ai_output->>total_carbon_footprint")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                return float(result.data[0]["total_carbon_footprint"])

        except Exception as e:
            print("History fetch failed:", e)

        return None

    # ----------------------------
    # Main orchestration
    # ----------------------------
    def analyze(
        self,
        request: AnalyzeRequest,
        user_id: Optional[str] = None,
        access_token: Optional[str] = None
    ) -> AnalyzeResponse:

        # Step 1: Normalize input
        processed_data = self.input_agent.process(request)

        # Step 2: Estimate emissions
        emissions = self.carbon_agent.calculate(processed_data)
        print("Emissions dict:", emissions)  # Debug: Check keys (e.g., 'total', 'transport', etc.)
        total_emissions = emissions.get("total", 0.0)  # Safe access; change "total" if key differs

        # Step 3: Generate recommendations
        recommendations = self.recommendation_agent.generate(
            processed_data,
            emissions
        )

        # Step 4: Fetch previous footprint (history)
        previous_total = self._get_previous_total(user_id, access_token)

        # Step 5: Generate explanation (LLM + history)
        explanation = self.explanation_agent.generate(
            processed_data=processed_data,
            emissions=emissions,
            total_emissions=total_emissions,
            recommendations=recommendations,
            previous_total=previous_total
        )

        # Filter category_emissions to exclude the total key
        category_emissions = {k: v for k, v in emissions.items() if k != "total"}

        return AnalyzeResponse(
            total_carbon_footprint=total_emissions,  # Fixed: Use total_emissions instead of undefined 'total'
            category_emissions=category_emissions,  # Use filtered dict
            top_recommendations=recommendations,
            explanation=explanation,
            user_id=user_id
        )