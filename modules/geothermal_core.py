
from dataclasses import dataclass
from typing import Dict

@dataclass
class GeothermalCoreInputs:
    geothermal_temperature_c: float
    reinjection_temperature_c: float
    flow_rate_kg_s: float
    steam_fraction_pct: float
    turbine_efficiency_pct: float
    generator_efficiency_pct: float
    plant_availability_pct: float
    parasitic_load_pct: float
    grid_export_pct: float
    internal_use_priority_pct: float
    electricity_price_chf_kwh: float
    avoided_internal_price_chf_kwh: float
    opex_chf_day: float
    turbine_maintenance_chf_day: float
    heat_recovery_efficiency_pct: float
    heat_value_chf_kwh: float
    co2_avoided_kg_mwh: float

def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))

def calculate(i: GeothermalCoreInputs) -> Dict[str, float]:
    cp_water = 4.18
    delta_t = max(0.0, i.geothermal_temperature_c - i.reinjection_temperature_c)
    thermal_kw = i.flow_rate_kg_s * cp_water * delta_t
    thermal_kwh_day = thermal_kw * 24.0 * clamp(i.plant_availability_pct) / 100.0

    steam_factor = clamp(i.steam_fraction_pct) / 100.0
    turbine_eff = clamp(i.turbine_efficiency_pct) / 100.0
    generator_eff = clamp(i.generator_efficiency_pct) / 100.0

    gross_electric_kwh_day = thermal_kwh_day * steam_factor * turbine_eff * generator_eff
    parasitic_kwh_day = gross_electric_kwh_day * clamp(i.parasitic_load_pct) / 100.0
    net_electric_kwh_day = max(0.0, gross_electric_kwh_day - parasitic_kwh_day)

    internal_priority = clamp(i.internal_use_priority_pct) / 100.0
    planned_internal_use = net_electric_kwh_day * internal_priority
    export_kwh_day = net_electric_kwh_day * clamp(i.grid_export_pct) / 100.0
    internal_use_kwh_day = max(0.0, net_electric_kwh_day - export_kwh_day)

    recoverable_heat_kwh_day = thermal_kwh_day * max(0.0, 1.0 - steam_factor * turbine_eff) * clamp(i.heat_recovery_efficiency_pct) / 100.0

    export_revenue = export_kwh_day * i.electricity_price_chf_kwh
    internal_savings = internal_use_kwh_day * i.avoided_internal_price_chf_kwh
    heat_value = recoverable_heat_kwh_day * i.heat_value_chf_kwh
    total_primary_value = export_revenue + internal_savings + heat_value

    total_opex = i.opex_chf_day + i.turbine_maintenance_chf_day
    net_primary_profit = total_primary_value - total_opex

    co2_avoided_kg_day = net_electric_kwh_day / 1000.0 * i.co2_avoided_kg_mwh
    cost_per_kwh_signal = total_opex / max(net_electric_kwh_day, 0.001)

    power_score = clamp(
        min(100.0, net_electric_kwh_day / 1000.0) * 0.25
        + clamp(i.turbine_efficiency_pct) * 0.25
        + clamp(i.generator_efficiency_pct) * 0.20
        + clamp(i.plant_availability_pct) * 0.20
        + max(0.0, 100.0 - clamp(i.parasitic_load_pct) * 4.0) * 0.10
    )

    profit_score = clamp(50.0 + net_primary_profit / 500.0)
    heat_integration_score = clamp(
        clamp(i.heat_recovery_efficiency_pct) * 0.45
        + min(100.0, recoverable_heat_kwh_day / max(thermal_kwh_day, 1.0) * 100.0) * 0.35
        + min(100.0, recoverable_heat_kwh_day / 3000.0) * 0.20
    )

    primary_engine_readiness = clamp(
        power_score * 0.40
        + profit_score * 0.35
        + heat_integration_score * 0.25
    )

    return {
        "thermal_kwh_day": thermal_kwh_day,
        "gross_electric_kwh_day": gross_electric_kwh_day,
        "parasitic_kwh_day": parasitic_kwh_day,
        "net_electric_kwh_day": net_electric_kwh_day,
        "export_kwh_day": export_kwh_day,
        "internal_use_kwh_day": internal_use_kwh_day,
        "planned_internal_use_kwh_day": planned_internal_use,
        "recoverable_heat_kwh_day": recoverable_heat_kwh_day,
        "export_revenue_chf_day": export_revenue,
        "internal_savings_chf_day": internal_savings,
        "heat_value_chf_day": heat_value,
        "total_primary_value_chf_day": total_primary_value,
        "total_opex_chf_day": total_opex,
        "net_primary_profit_chf_day": net_primary_profit,
        "co2_avoided_kg_day": co2_avoided_kg_day,
        "cost_per_kwh_signal_chf": cost_per_kwh_signal,
        "power_score": power_score,
        "profit_score": profit_score,
        "heat_integration_score": heat_integration_score,
        "primary_engine_readiness": primary_engine_readiness,
    }

def interpretation(r):
    if r["net_primary_profit_chf_day"] > 0 and r["primary_engine_readiness"] >= 75:
        return "Strong geothermal core scenario. The primary power engine can generate electricity value, internal savings and recoverable heat for downstream modules."
    if r["net_primary_profit_chf_day"] <= 0:
        return "The geothermal core is not yet profitable. Increase net power output, electricity value, plant availability or reduce OPEX."
    if r["power_score"] < 65:
        return "Power generation is the limiting factor. Improve temperature, flow, turbine efficiency, generator efficiency or reduce parasitic load."
    if r["heat_integration_score"] < 60:
        return "Heat integration is weak. Improve recoverable heat efficiency because downstream desalination and steam preparation depend on it."
    return "Promising geothermal-first scenario. Optimize turbine/generator performance and heat recovery before connecting downstream modules."
