# HydrogenOrg V4.0 — Geothermal Core Main Simulator

This is the primary simulator for the HydrogenOrg engineering pathway.

Primary chain:

Geothermal heat -> high-pressure steam -> turbine -> generator -> clean electricity.

Downstream chain:

Electricity + recoverable heat -> desalination -> pure water -> steam preparation -> plasma reactor -> hydrogen fuel.

## Run locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Disclaimer

This simulator is conceptual and does not represent certified industrial or financial performance data.


## Display fix

Recoverable heat is displayed in GWh/day in the main dashboard to avoid truncation.
