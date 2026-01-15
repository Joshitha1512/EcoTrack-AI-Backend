import os
from typing import Dict, List, Optional

from schemas import Recommendation

try:
    from groq import Groq
except ImportError:
    Groq = None


class ExplanationAgent:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if self.api_key and Groq:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    # ----------------------------
    # Main explanation generator
    # ----------------------------
    def generate(
        self,
        processed_data: Dict,
        emissions: Dict,
        total_emissions: float,
        recommendations: List[Recommendation],
        previous_total: Optional[float] = None
    ) -> str:

        # -------- LLM PATH --------
        if self.client:
            try:
                prompt = self._build_prompt(
                    emissions,
                    total_emissions,
                    recommendations,
                    previous_total
                )

                completion = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a friendly climate sustainability assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.5,
                    max_tokens=200,
                )

                explanation = completion.choices[0].message.content.strip()

                # Ensure required headers exist
                if all(
                    key in explanation
                    for key in [
                        "Introduction:",
                        "Emission Breakdown:",
                        "Recommendations:",
                        "Conclusion:"
                    ]
                ):
                    return explanation

            except Exception as e:
                print("Groq LLM failed, using fallback:", e)

        # -------- FALLBACK --------
        return self._fallback_explanation(
            emissions,
            total_emissions,
            recommendations,
            previous_total
        )

    # ----------------------------
    # Prompt builder
    # ----------------------------
    def _build_prompt(
        self,
        emissions: Dict,
        total: float,
        recommendations: List[Recommendation],
        previous_total: Optional[float]
    ) -> str:

        rec_text = "\n".join(
            f"- {r.title}: {r.description} (Potential savings: {r.potential_savings:.1f} kg CO2)"
            for r in recommendations
        )

        history_text = (
            f"The user's previous recorded carbon footprint was {previous_total:.1f} kg CO2."
            if previous_total
            else "This is the user's first recorded carbon footprint."
        )

        return f"""
A user has an annual carbon footprint of {total:.1f} kg CO2.
{history_text}

Category breakdown:
- Transport: {emissions['transport']:.1f} kg
- Electricity: {emissions['electricity']:.1f} kg
- Diet: {emissions['diet']:.1f} kg

Top recommendations:
{rec_text}

Write a concise, user-friendly explanation using EXACTLY this structure:

Introduction:
- 1 short sentence stating the total footprint and encouraging the user.

Emission Breakdown:
- 2 short sentences explaining which category contributes the most and why.

Recommendations:
- For EACH recommendation, write ONLY ONE sentence explaining why it helps and one concrete action.

Conclusion:
- 1 short motivational sentence.

Rules:
- Maximum 150 words TOTAL
- No percentages unless necessary
- Do NOT exaggerate savings
- Be clear, simple, and encouraging
"""

    # ----------------------------
    # Structured deterministic fallback
    # ----------------------------
    def _fallback_explanation(
        self,
        emissions: Dict,
        total: float,
        recommendations: List[Recommendation],
        previous_total: Optional[float]
    ) -> str:

        sorted_categories = sorted(
            emissions.items(),
            key=lambda x: x[1],
            reverse=True
        )

        largest_category, largest_value = sorted_categories[0]

        rec_lines = "\n".join(
            f"- {r.title}: Focus on small habit changes that reduce emissions in this area."
            for r in recommendations
        )

        history_line = (
            f" Compared to your previous footprint of {previous_total:.1f} kg CO2, "
            f"this is a change of {total - previous_total:+.1f} kg."
            if previous_total
            else ""
        )

        return f"""
Introduction:
Your annual carbon footprint is approximately {total:.1f} kg CO2.{history_line}

Emission Breakdown:
The largest contribution comes from {largest_category}, making it the most impactful area to improve.
Reducing emissions here can significantly lower your overall footprint.

Recommendations:
{rec_lines}

Conclusion:
Small, consistent actions can make a meaningful difference over time.
""".strip()
