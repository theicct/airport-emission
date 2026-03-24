from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parent
SECRETS_PATH = ROOT / ".streamlit" / "secrets.toml"
OUTPUT_PATH = ROOT / "config.js"


def read_google_maps_key() -> str:
    if not SECRETS_PATH.exists():
        raise FileNotFoundError(f"Missing secrets file: {SECRETS_PATH}")

    with SECRETS_PATH.open("rb") as handle:
        data = tomllib.load(handle)

    api_key = data.get("GOOGLE_MAPS_API_KEY", "")

    if isinstance(api_key, dict):
        api_key = api_key.get("api_key") or api_key.get("key") or ""

    if not api_key:
        raise KeyError("GOOGLE_MAPS_API_KEY is missing in .streamlit/secrets.toml")

    return str(api_key)


def main() -> None:
    api_key = read_google_maps_key()
    OUTPUT_PATH.write_text(
        'window.AIRLIFT_CONFIG = {\n'
        f'  googleMapsApiKey: "{api_key}",\n'
        '};\n',
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
