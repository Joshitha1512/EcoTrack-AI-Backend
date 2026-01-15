"""
ExplanationAgent: Explains emissions and recommendations using LLM (Groq)
with deterministic ranking and safe fallback.
"""

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

        # -------- Deterministic ranking (CRITICAL FIX) --------
        largest_category = max(emissions, key=emissions.get)
        largest_value = emissions[largest_category]

        # -------- LLM PATH --------
        if self.client:
            try:
                prompt = self._build_prompt(
                    emissions=emissions,
                    total=total_emissions,
                    recommendations=recommendations,
                    previous_total=previous_total,
                    largest_category=largest_category,
                    largest_value=largest_value,
                )

                completion = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a clear, accurate climate sustainability assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,   # lower = more stable
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
        largest_category: str,
        largest_value: float
    ) -> str:

        rec_text = "\n".join(
            f"- {r.title}: {r.description}"
            for r in recommendations
        )

        return f"""
A user has an annual carbon footprint of {total:.1f} kg CO2.

Category breakdown (already calculated — do NOT reinterpret):
- Transport: {emissions['transport']:.1f} kg
- Electricity: {emissions['electricity']:.1f} kg
- Diet: {emissions['diet']:.1f} kg

The largest contributing category is:
- {largest_category.capitalize()} at {largest_value:.1f} kg CO2

Top recommendations:
{rec_text}

Write using EXACTLY this structure:

Introduction:
- One short encouraging sentence mentioning the total footprint.

Emission Breakdown:
- One sentence stating that {largest_category} is the largest contributor.
- One sentence briefly explaining why this category is high.

Recommendations:
- Each recommendation must be a separate bullet starting with "- "
- One sentence per bullet.

Conclusion:
- One short motivational sentence.

STRICT RULES:
- NEVER invent categories
- NEVER mention "total" as a category
- Use ONLY: transport, electricity, diet
- Do NOT change the ranking
- Do NOT use percentages
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
            f"The largest contributor is {max_category}.{history_line} "
            f"Focusing on improvements in this area can significantly reduce your impact."
        )
