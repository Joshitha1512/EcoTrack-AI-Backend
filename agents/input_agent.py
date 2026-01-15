"""InputAgent: Validates and normalizes incoming lifestyle data"""

from typing import Dict, Any
from schemas import AnalyzeRequest


class InputAgent:
    """
    Agent responsible for validating and normalizing incoming lifestyle data.
    
    This agent ensures all input values are structured, consistent, and ready
    for downstream processing by other agents in the system.
    """
    
    def process(self, request: AnalyzeRequest) -> Dict[str, Any]:
        """
        Validate and normalize incoming lifestyle data.
        
        Agentic Behavior:
        - Validates all input fields to ensure data integrity
        - Normalizes values to consistent formats and ranges
        - Ensures structured output for downstream agents
        
        Args:
            request: The analyze request containing raw user lifestyle data
            
        Returns:
            Dictionary with validated, normalized, and structured data
        """
        # Validate and normalize transport data
        # Ensure all values are non-negative and properly structured
        transport_data = {
            "car_miles_per_week": max(0.0, request.transport.car_miles_per_week or 0.0),
            "public_transit_trips_per_week": max(0, request.transport.public_transit_trips_per_week or 0),
            "flights_per_year": max(0, request.transport.flights_per_year or 0),
        }
        
        # Validate and normalize electricity data
        # Ensure kWh is non-negative and energy source has a default value
        electricity_data = {
            "monthly_kwh": max(0.0, request.electricity.monthly_kwh or 0.0),
            "energy_source": (request.electricity.energy_source or "grid").lower(),
        }
        
        # Validate and normalize diet data
        # Ensure percentages are within valid range (0-100) and meals count is reasonable
        diet_data = {
            "meals_per_week": max(0, request.diet.meals_per_week or 21),
            "meat_percentage": max(0.0, min(100.0, request.diet.meat_percentage or 0.0)),
            "vegetarian_percentage": max(0.0, min(100.0, request.diet.vegetarian_percentage or 0.0)),
            "vegan_percentage": max(0.0, min(100.0, request.diet.vegan_percentage or 0.0)),
        }
        
        # Normalize diet percentages to ensure they sum to 100%
        # This ensures consistency for downstream calculations
        total_percentage = (
            diet_data["meat_percentage"] + 
            diet_data["vegetarian_percentage"] + 
            diet_data["vegan_percentage"]
        )
        if total_percentage > 0:
            scale = 100.0 / total_percentage
            diet_data["meat_percentage"] *= scale
            diet_data["vegetarian_percentage"] *= scale
            diet_data["vegan_percentage"] *= scale
        else:
            # Default to balanced distribution if no percentages provided
            diet_data["meat_percentage"] = 33.33
            diet_data["vegetarian_percentage"] = 33.33
            diet_data["vegan_percentage"] = 33.34
        
        # Return structured, validated data for next agent in the pipeline
        return {
            "transport": transport_data,
            "electricity": electricity_data,
            "diet": diet_data,
        }

