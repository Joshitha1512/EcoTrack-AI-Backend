"""ExplanationAgent: Explains why recommended actions help reduce emissions"""
"""ExplanationAgent: Uses LLM (Groq) with safe fallback"""

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

        # ✅ Determine largest category deterministically
        largest_category = max(emissions, key=emissions.get)

        # -------- LLM PATH --------
        if self.client:
            try:
                prompt = self._build_prompt(
                    emissions,
                    total_emissions,
                    recommendations,
                    previous_total,
                    largest_category
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
                    temperature=0.4,
                    max_tokens=200,
                )

                explanation = completion.choices[0].message.content.strip()

                if explanation:
                    return explanation

            except Exception as e:
                print("Groq LLM failed, using fallback:", e)

        # -------- FALLBACK --------
        return self._fallback_explanation(emissions, total_emissions, previous_total)

    # ----------------------------
    # Prompt builder
    # ----------------------------
    def _build_prompt(
        self,
        emissions: Dict,
        total: float,
        recommendations: List[Recommendation],
        previous_total: Optional[float],
        largest_category: str
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

The largest contributing category is FIXED as "{largest_category}".

Top recommendations:
{rec_text}

Write a concise, user-friendly explanation using EXACTLY this structure:

Introduction:
- 1 short sentence stating the total footprint and encouraging the user.

Emission Breakdown:
- The largest contributing category is "{largest_category}".
- Write exactly 2 short sentences explaining WHY this category is the largest.
- Do NOT choose or infer any other category.

Recommendations:
- For EACH recommendation, write ONLY ONE sentence explaining why it helps and one concrete action.

Conclusion:
- 1 short motivational sentence.

Rules:
- Maximum 150 words TOTAL
- Do NOT calculate or infer rankings
- Do NOT invent percentages
- Use the provided largest category exactly
- Be clear, simple, and encouraging
"""

    # ----------------------------
    # Deterministic fallback
    # ----------------------------
    def _fallback_explanation(
        self,
        emissions: Dict,
        total: float,
        previous_total: Optional[float]
    ) -> str:

        max_category = max(emissions, key=emissions.get)

        history_line = (
            f" Compared to your previous footprint of {previous_total:.1f} kg CO2, "
            f"this shows a change of {total - previous_total:+.1f} kg."
            if previous_total
            else ""
        )

        return (
            f"Your total carbon footprint is {total:.1f} kg CO2 per year. "
            f"The largest contribution comes from {max_category}.{history_line} "
            f"Focusing on improvements in this area can significantly reduce your impact."
        )
