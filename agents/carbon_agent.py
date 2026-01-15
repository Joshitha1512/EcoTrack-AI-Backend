"""CarbonEstimationAgent: Calculates carbon footprint using mock emission factors"""

from typing import Dict, Any


class CarbonEstimationAgent:
    """
    Agent responsible for calculating carbon footprint using mock emission factors.
    
    This agent uses standardized emission factors to compute category-wise emissions
    and calculates the total carbon footprint for the user.
    """
    
    # Mock carbon emission factors (kg CO2 per unit)
    # These are simplified factors for demonstration purposes
    CAR_EMISSION_FACTOR = 0.411  # kg CO2 per mile (average car)
    PUBLIC_TRANSIT_FACTOR = 0.05  # kg CO2 per trip (average public transit)
    FLIGHT_FACTOR = 250.0  # kg CO2 per flight (average short-haul flight)
    
    GRID_ELECTRICITY_FACTOR = 0.5  # kg CO2 per kWh (grid average)
    SOLAR_FACTOR = 0.05  # kg CO2 per kWh (solar with manufacturing)
    WIND_FACTOR = 0.02  # kg CO2 per kWh (wind with manufacturing)
    
    MEAT_MEAL_FACTOR = 5.0  # kg CO2 per meal with meat
    VEGETARIAN_MEAL_FACTOR = 2.0  # kg CO2 per vegetarian meal
    VEGAN_MEAL_FACTOR = 1.0  # kg CO2 per vegan meal
    
    def calculate(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate category-wise emissions and total carbon footprint.
        
        Agentic Behavior:
        - Uses mock emission factors to calculate emissions for each category
        - Computes transport, electricity, and diet emissions separately
        - Calculates total carbon footprint by summing all categories
        
        Args:
            processed_data: Validated and normalized data from InputAgent
            
        Returns:
            Dictionary containing:
            - category_emissions: Dict with transport, electricity, diet emissions
            - total_emissions: Total carbon footprint in kg CO2/year
        """
        # Calculate category-wise emissions using mock factors
        transport_emissions = self._calculate_transport(processed_data["transport"])
        electricity_emissions = self._calculate_electricity(processed_data["electricity"])
        diet_emissions = self._calculate_diet(processed_data["diet"])
        
        # Compute total carbon footprint
        total_emissions = transport_emissions + electricity_emissions + diet_emissions
        
        return {
            "transport": transport_emissions,
            "electricity": electricity_emissions,
            "diet": diet_emissions,
            "total": total_emissions,
        }
    
    def _calculate_transport(self, transport_data: Dict[str, Any]) -> float:
        """
        Calculate transport-related carbon emissions using mock factors.
        
        Uses emission factors to compute annual emissions from:
        - Car travel (miles/week converted to annual)
        - Public transit trips (trips/week converted to annual)
        - Air travel (flights per year)
        """
        # Car emissions: miles/week * 52 weeks/year * emission factor
        car_emissions = (
            transport_data["car_miles_per_week"] * 52 * self.CAR_EMISSION_FACTOR
        )
        
        # Public transit emissions: trips/week * 52 weeks/year * emission factor
        transit_emissions = (
            transport_data["public_transit_trips_per_week"] * 52 * self.PUBLIC_TRANSIT_FACTOR
        )
        
        # Flight emissions: flights/year * emission factor per flight
        flight_emissions = (
            transport_data["flights_per_year"] * self.FLIGHT_FACTOR
        )
        
        return car_emissions + transit_emissions + flight_emissions
    
    def _calculate_electricity(self, electricity_data: Dict[str, Any]) -> float:
        """
        Calculate electricity-related carbon emissions using mock factors.
        
        Selects appropriate emission factor based on energy source:
        - Grid: highest emissions
        - Solar: lower emissions (includes manufacturing impact)
        - Wind: lowest emissions (includes manufacturing impact)
        """
        monthly_kwh = electricity_data["monthly_kwh"]
        energy_source = electricity_data["energy_source"].lower()
        
        # Select emission factor based on energy source
        if energy_source == "solar":
            factor = self.SOLAR_FACTOR
        elif energy_source == "wind":
            factor = self.WIND_FACTOR
        else:  # grid or default
            factor = self.GRID_ELECTRICITY_FACTOR
        
        # Calculate annual emissions: monthly_kwh * 12 months * emission factor
        return monthly_kwh * 12 * factor
    
    def _calculate_diet(self, diet_data: Dict[str, Any]) -> float:
        """
        Calculate diet-related carbon emissions using mock factors.
        
        Uses different emission factors for:
        - Meat meals: highest emissions
        - Vegetarian meals: moderate emissions
        - Vegan meals: lowest emissions
        """
        meals_per_week = diet_data["meals_per_week"]
        meat_pct = diet_data["meat_percentage"] / 100.0
        vegetarian_pct = diet_data["vegetarian_percentage"] / 100.0
        vegan_pct = diet_data["vegan_percentage"] / 100.0
        
        # Calculate meals per category per week
        meat_meals = meals_per_week * meat_pct
        vegetarian_meals = meals_per_week * vegetarian_pct
        vegan_meals = meals_per_week * vegan_pct
        
        # Calculate weekly emissions using category-specific factors
        weekly_emissions = (
            meat_meals * self.MEAT_MEAL_FACTOR +
            vegetarian_meals * self.VEGETARIAN_MEAL_FACTOR +
            vegan_meals * self.VEGAN_MEAL_FACTOR
        )
        
        # Convert to annual emissions: weekly * 52 weeks/year
        return weekly_emissions * 52

