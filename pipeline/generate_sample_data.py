"""
Generate synthetic SEMO-format DAM pricing data for pipeline testing.
Run once to create a sample CSV in data/, then use the pipeline scripts against it.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def generate_dam_day(date_str: str, wind_factor: float = 0.5) -> pd.DataFrame:
    """
    Generate one day of synthetic DAM prices (48 half-hour periods).
    
    wind_factor: 0.0 = no wind (high prices), 1.0 = very windy (low prices)
    """
    periods = pd.date_range(date_str, periods=48, freq="30min")
    
    # Base demand shape: low overnight, morning ramp, afternoon plateau, evening peak
    hour = np.array([t.hour + t.minute / 60 for t in periods])
    demand_shape = (
        30
        + 40 * np.exp(-0.5 * ((hour - 8.5) / 2) ** 2)   # morning peak
        + 60 * np.exp(-0.5 * ((hour - 17.5) / 1.5) ** 2) # evening peak
        + 20 * np.exp(-0.5 * ((hour - 13) / 3) ** 2)      # afternoon plateau
    )
    
    # Wind suppresses prices
    wind_suppression = wind_factor * 35
    base_price = demand_shape - wind_suppression
    
    # Add noise
    noise = np.random.normal(0, 8, size=48)
    prices = np.maximum(base_price + noise, -5)  # floor at -5 (negative prices happen)
    
    # Wind generation as % of demand (synthetic)
    wind_pct = np.clip(
        wind_factor * 60 + np.random.normal(0, 8, size=48),
        5, 85
    )
    
    # System demand (MW)
    demand_mw = 2800 + 1800 * (demand_shape - demand_shape.min()) / (demand_shape.max() - demand_shape.min())
    demand_mw += np.random.normal(0, 50, size=48)
    
    return pd.DataFrame({
        "DeliveryDate": [date_str] * 48,
        "Period": range(1, 49),
        "StartTime": [t.strftime("%H:%M") for t in periods],
        "DAMPrice_EUR_MWh": prices.round(2),
        "WindGeneration_pct": wind_pct.round(1),
        "SystemDemand_MW": demand_mw.round(0),
    })


def generate_sample_data():
    """Generate 7 days of sample data with varying wind conditions."""
    np.random.seed(42)
    
    dates_and_wind = [
        ("2026-04-10", 0.7),  # windy day
        ("2026-04-11", 0.6),
        ("2026-04-12", 0.3),  # low wind
        ("2026-04-13", 0.15), # very low wind - expect high prices
        ("2026-04-14", 0.5),
        ("2026-04-15", 0.8),  # very windy
        ("2026-04-16", 0.4),
    ]
    
    frames = [generate_dam_day(d, w) for d, w in dates_and_wind]
    df = pd.concat(frames, ignore_index=True)
    
    outpath = DATA_DIR / "semo_dam_sample.csv"
    df.to_csv(outpath, index=False)
    print(f"Generated {len(df)} rows -> {outpath}")
    return outpath


if __name__ == "__main__":
    generate_sample_data()
