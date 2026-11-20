"""Functions to load and merge country and indicator data from World Bank API."""

from pathlib import Path
import pandas as pd
import requests


COUNTRIES_URL = "https://api.worldbank.org/v2/country?format=json&per_page=300"
POP_URL = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000&mrv=5"
GDP_URL = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD?format=json&per_page=20000&mrv=5"
CACHE_FILE = Path("data/countries.csv")


def get_countries_df() -> pd.DataFrame:
    """Download countries, capitals, regions, and coordinates from World Bank API."""
    response = requests.get(COUNTRIES_URL, timeout=15)
    response.raise_for_status()
    payload = response.json()

    rows = []
    if isinstance(payload, list) and len(payload) > 1 and payload[1]:
        for item in payload[1]:
            if not isinstance(item, dict):
                continue

            region_info = item.get("region") or {}
            # Skip regional and income groups (region id == "NA")
            if region_info.get("id") == "NA":
                continue

            code = item.get("id")
            name = item.get("name")
            capital = (item.get("capitalCity") or "").strip()
            region = (region_info.get("value") or "").strip()

            if code and name and capital and region:
                rows.append(
                    {
                        "code": str(code).strip(),
                        "country": str(name).strip(),
                        "capital": capital,
                        "region": region,
                        "latitude": pd.to_numeric(item.get("latitude"), errors="coerce"),
                        "longitude": pd.to_numeric(item.get("longitude"), errors="coerce"),
                    }
                )

    df = pd.DataFrame(rows)
    if not df.empty:
        df = (
            df.drop_duplicates(subset=["code"])
            .dropna(subset=["latitude", "longitude"])
            .reset_index(drop=True)
        )
    return df


def get_indicator_df(url: str, col_name: str) -> pd.DataFrame:
    """Download the latest non-null value of a World Bank indicator per country."""
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()

    rows = []
    if isinstance(payload, list) and len(payload) > 1 and payload[1]:
        for entry in payload[1]:
            code = entry.get("countryiso3code")
            value = entry.get("value")
            year = entry.get("date")
            if code and value is not None and year is not None:
                rows.append(
                    {"code": str(code).strip(), "year": int(year), col_name: float(value)}
                )

    if not rows:
        return pd.DataFrame(columns=["code", col_name])

    df_ind = pd.DataFrame(rows)
    df_ind = df_ind.sort_values("year", ascending=False)
    df_ind = df_ind.drop_duplicates(subset=["code"])
    return df_ind[["code", col_name]]


def load_data(use_cache: bool = True) -> pd.DataFrame:
    """Load merged country dataset from CSV cache or download it from World Bank API."""
    if use_cache and CACHE_FILE.exists():
        return pd.read_csv(CACHE_FILE)

    try:
        countries = get_countries_df()
        pop = get_indicator_df(POP_URL, "population")
        gdp = get_indicator_df(GDP_URL, "gdp_per_capita")
    except requests.RequestException as error:
        raise RuntimeError(f"Failed to load data from World Bank API: {error}") from error

    df = pd.merge(countries, pop, on="code", how="left")
    df = pd.merge(df, gdp, on="code", how="left")
    df["gdp_per_capita"] = df["gdp_per_capita"].round(2)

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CACHE_FILE, index=False)
    return df