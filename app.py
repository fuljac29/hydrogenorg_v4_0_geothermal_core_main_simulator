import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules.geothermal_core import GeothermalCoreInputs, calculate, interpretation

st.set_page_config(page_title="HydrogenOrg V4.0 Geothermal Core Main Simulator", page_icon="⚡", layout="wide")

st.title("HydrogenOrg V4.0 — Geothermal Core Main Simulator")
st.subheader("Primary simulator: geothermal electricity first, downstream hydrogen fuel second")
st.info("This is the main HydrogenOrg simulator. It models geothermal electricity generation as the primary economic engine before connecting desalination, steam preparation, plasma hydrogen, gas separation and mobility fuel layers.")

with st.expander("Base concept", expanded=True):
    st.markdown("""
**Primary chain**

Geothermal heat → high-pressure steam → turbine → electric generator → clean electricity

**Downstream chain**

Electricity + recovered heat → desalination → pure water → steam preparation → plasma reactor → hydrogen fuel

The system must first generate stable economic value through geothermal electricity.  
Hydrogen becomes the strategic clean fuel layer for heavy vehicles, ships, ports, cargo and future aviation.
""")

with st.sidebar:
    st.header("Geothermal core inputs")

    st.subheader("Resource and steam")
    temp = st.slider("Geothermal source temperature (°C)", 80, 380, 220, 5)
    reinj = st.slider("Reinjection temperature (°C)", 30, 180, 80, 5)
    flow = st.slider("Geothermal flow rate (kg/s)", 10.0, 1000.0, 135.0, 5.0)
    steam_fraction = st.slider("Steam / usable conversion fraction (%)", 5, 90, 42, 1)

    st.subheader("Turbine and generator")
    turbine = st.slider("Turbine efficiency (%)", 5, 60, 34, 1)
    generator = st.slider("Generator efficiency (%)", 60, 99, 94, 1)
    availability = st.slider("Plant availability (%)", 40, 100, 92, 1)
    parasitic = st.slider("Parasitic load (%)", 0, 40, 8, 1)

    st.subheader("Electricity use")
    export_pct = st.slider("Electricity exported to grid (%)", 0, 100, 72, 1)
    internal_priority = st.slider("Internal use priority signal (%)", 0, 100, 28, 1)
    electricity_price = st.slider("Grid export price (CHF/kWh)", 0.01, 1.00, 0.16, 0.01)
    avoided_price = st.slider("Internal avoided electricity cost (CHF/kWh)", 0.01, 1.00, 0.22, 0.01)

    st.subheader("Costs and heat")
    opex = st.slider("Geothermal plant OPEX (CHF/day)", 0, 50000, 4200, 100)
    maintenance = st.slider("Turbine/generator maintenance (CHF/day)", 0, 50000, 1800, 100)
    heat_recovery = st.slider("Heat recovery efficiency (%)", 0, 95, 68, 1)
    heat_value = st.slider("Recovered heat value (CHF/kWh thermal)", 0.000, 0.300, 0.025, 0.005)
    co2_factor = st.slider("CO₂ avoided signal (kg CO₂/MWh)", 0, 1000, 450, 10)

inputs = GeothermalCoreInputs(
    temp, reinj, flow, steam_fraction, turbine, generator, availability, parasitic,
    export_pct, internal_priority, electricity_price, avoided_price, opex, maintenance,
    heat_recovery, heat_value, co2_factor
)

r = calculate(inputs)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Net electricity", f"{r['net_electric_kwh_day']:.0f} kWh/day", "primary output")
c2.metric("Grid export", f"{r['export_kwh_day']:.0f} kWh/day", f"CHF {r['export_revenue_chf_day']:.0f}/day")
c3.metric("Internal electricity", f"{r['internal_use_kwh_day']:.0f} kWh/day", f"CHF {r['internal_savings_chf_day']:.0f}/day saved")
c4.metric("Recoverable heat", f"{r['recoverable_heat_kwh_day']/1000000:.2f} GWh/day", f"CHF {r['heat_value_chf_day']:.0f}/day")
c5.metric("Primary profit", f"CHF {r['net_primary_profit_chf_day']:.0f}/day", f"{r['primary_engine_readiness']:.0f}/100 readiness")

tabs = st.tabs([
    "Overview",
    "Power generation",
    "Profitability",
    "Downstream connections",
    "Environmental signal",
    "Export to V4.1–V4.7b",
    "Engineering priorities"
])

with tabs[0]:
    st.header("Geothermal-first economic engine")
    st.markdown("""
HydrogenOrg should be presented as a geothermal-first regenerative infrastructure.

The first engineering objective is not hydrogen alone.  
The first objective is a stable geothermal power plant that produces clean electricity and useful heat.

Hydrogen, desalination, oxygen, salt recovery and mobility fuel become connected value layers.
""")
    st.success(interpretation(r))

with tabs[1]:
    st.header("Power generation balance")
    df = pd.DataFrame({
        "Metric": [
            "Thermal energy input",
            "Gross electricity",
            "Parasitic load",
            "Net electricity",
            "Grid export",
            "Internal electricity",
            "Recoverable heat",
            "Cost per kWh signal",
            "Power score",
        ],
        "Value": [
            f"{r['thermal_kwh_day']:.1f} kWh/day",
            f"{r['gross_electric_kwh_day']:.1f} kWh/day",
            f"{r['parasitic_kwh_day']:.1f} kWh/day",
            f"{r['net_electric_kwh_day']:.1f} kWh/day",
            f"{r['export_kwh_day']:.1f} kWh/day",
            f"{r['internal_use_kwh_day']:.1f} kWh/day",
            f"{r['recoverable_heat_kwh_day']/1000000:.2f} GWh/day",
            f"CHF {r['cost_per_kwh_signal_chf']:.3f}/kWh",
            f"{r['power_score']:.1f}/100",
        ]
    })
    st.dataframe(df, use_container_width=True)

with tabs[2]:
    st.header("Primary profitability")
    df = pd.DataFrame({
        "Revenue / cost": [
            "Electricity export revenue",
            "Internal electricity savings",
            "Recovered heat value",
            "Total primary value",
            "OPEX + turbine maintenance",
            "Net primary profit",
            "Profit score",
            "Primary engine readiness",
        ],
        "CHF/day or score": [
            f"CHF {r['export_revenue_chf_day']:.2f}/day",
            f"CHF {r['internal_savings_chf_day']:.2f}/day",
            f"CHF {r['heat_value_chf_day']:.2f}/day",
            f"CHF {r['total_primary_value_chf_day']:.2f}/day",
            f"CHF {r['total_opex_chf_day']:.2f}/day",
            f"CHF {r['net_primary_profit_chf_day']:.2f}/day",
            f"{r['profit_score']:.1f}/100",
            f"{r['primary_engine_readiness']:.1f}/100",
        ]
    })
    st.dataframe(df, use_container_width=True)

    chart = pd.DataFrame({
        "Layer": ["Export", "Internal savings", "Heat value", "OPEX"],
        "CHF/day": [
            r["export_revenue_chf_day"],
            r["internal_savings_chf_day"],
            r["heat_value_chf_day"],
            -r["total_opex_chf_day"],
        ]
    })
    fig, ax = plt.subplots()
    ax.bar(chart["Layer"], chart["CHF/day"])
    ax.set_ylabel("CHF/day")
    ax.set_title("Primary geothermal value balance")
    st.pyplot(fig)

with tabs[3]:
    st.header("Connections to downstream simulators")
    st.markdown("""
The geothermal core exports values to the downstream engineering chain:

- **V4.2b Desalination** receives electricity and recoverable heat.
- **V4.3 Steam feed** receives purified water and heat for preheating.
- **V4.4 Plasma reactor** receives internally generated electricity and steam.
- **V4.5 Gas separation** receives power and thermal support.
- **V4.6 Thermal recovery** sends heat back to the core integration layer.
- **V4.7b Profitability** uses geothermal export revenue as the primary economic driver.
""")

with tabs[4]:
    st.header("Environmental signal")
    st.dataframe(pd.DataFrame({
        "Metric": ["CO₂ avoided signal", "Clean electricity", "Recoverable heat", "Conceptual environmental role"],
        "Value": [
            f"{r['co2_avoided_kg_day']:.1f} kg CO₂/day",
            f"{r['net_electric_kwh_day']:.1f} kWh/day",
            f"{r['recoverable_heat_kwh_day']:.1f} kWh/day",
            "Replace fossil electricity, support clean water and produce hydrogen fuel",
        ]
    }), use_container_width=True)

with tabs[5]:
    st.header("Export JSON")
    st.json({
        "module": "V4.0 Geothermal Core Main Simulator",
        "net_electric_kwh_day": round(r["net_electric_kwh_day"], 2),
        "grid_export_kwh_day": round(r["export_kwh_day"], 2),
        "internal_use_kwh_day": round(r["internal_use_kwh_day"], 2),
        "recoverable_heat_kwh_day": round(r["recoverable_heat_kwh_day"], 2),
        "recoverable_heat_gwh_day": round(r["recoverable_heat_kwh_day"] / 1000000, 3),
        "export_revenue_chf_day": round(r["export_revenue_chf_day"], 2),
        "internal_savings_chf_day": round(r["internal_savings_chf_day"], 2),
        "heat_value_chf_day": round(r["heat_value_chf_day"], 2),
        "net_primary_profit_chf_day": round(r["net_primary_profit_chf_day"], 2),
        "co2_avoided_kg_day": round(r["co2_avoided_kg_day"], 2),
        "power_score": round(r["power_score"], 1),
        "profit_score": round(r["profit_score"], 1),
        "heat_integration_score": round(r["heat_integration_score"], 1),
        "primary_engine_readiness": round(r["primary_engine_readiness"], 1),
    })

with tabs[6]:
    st.header("Engineering priorities")
    st.markdown("""
### Primary module priorities

1. Characterize geothermal source temperature, flow and reinjection temperature.  
2. Size the steam turbine and generator before sizing the hydrogen layer.  
3. Maximize net electricity and reduce parasitic load.  
4. Use electricity export and internal savings as the first economic engine.  
5. Recover heat for desalination and steam preparation.  
6. Connect purified water and steam production to the hydrogen fuel layer.  
7. Treat H₂ as strategic clean fuel for heavy transport, maritime logistics and future aviation.  
8. Use open simulation before industrial claims or investment claims.
""")

st.markdown("---")
st.caption("HydrogenOrg V4.0 is a conceptual geothermal-first engineering simulator. It does not represent certified industrial or financial performance data.")
