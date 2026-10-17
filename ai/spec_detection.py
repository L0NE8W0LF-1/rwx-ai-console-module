import argparse
import json
from pathlib import Path

DEFAULT_RULES = {
    "console": {"recovery": 0.95, "normal": 0.9, "fault": 0.65},
    "xbox": {"recovery": 0.95, "normal": 0.90, "fault": 0.65},
    "playstation": {"recovery": 0.95, "normal": 0.90, "fault": 0.60},
    "nintendo": {"recovery": 0.90, "normal": 0.85, "fault": 0.55},
    "pc": {"recovery": 0.80, "normal": 0.75, "fault": 0.50},
}

PLATFORM_ALIASES = {
    "pc": "pc",
    "computer": "pc",
    "desktop": "pc",
    "laptop": "pc",
    "notebook": "pc",
    "dell": "pc",
    "lenovo": "pc",
    "hp": "pc",
    "hewlett-packard": "pc",
    "apple": "pc",
    "macbook": "pc",
    "asus": "pc",
    "acer": "pc",
    "msi": "pc",
    "surface": "pc",
    "alienware": "pc",
    "thinkpad": "pc",
    "xps": "pc",
}


def normalize_platform(profile):
    platform = str(profile.get("platform", "pc")).strip().lower()
    brand = str(profile.get("brand", "")).strip().lower()
    for source in (brand, platform):
        if not source:
            continue
        resolved = PLATFORM_ALIASES.get(source)
        if resolved:
            return resolved
    return platform or "pc"


def load_profile(path: str):
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Profile file not found: {path}")
    with file_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def score_profile(profile):
    platform = normalize_platform(profile)
    boot_state = str(profile.get("boot_state", "unknown")).lower()
    rules = DEFAULT_RULES.get(platform, DEFAULT_RULES["pc"])
    score = rules.get(boot_state, 0.5)

    if profile.get("cpu"):
        score += 0.02
    if profile.get("gpu"):
        score += 0.02
    if profile.get("storage_gb"):
        score += 0.01
    if profile.get("ram_gb"):
        score += 0.01

    return round(min(score, 1.0), 3)


def recommend_action(profile):
    score = score_profile(profile)
    if score >= 0.9:
        return "Load approved recovery image and continue diagnostics."
    if score >= 0.75:
        return "Inspect hardware metadata and verify device state before writing any payload."
    return "Device is in an elevated risk state; stop and validate target health before recovery."


def main():
    parser = argparse.ArgumentParser(description="RWX AI profile analyzer")
    parser.add_argument("--profile", required=True, help="Path to a JSON hardware profile")
    args = parser.parse_args()

    profile = load_profile(args.profile)
    score = score_profile(profile)
    action = recommend_action(profile)

    print(json.dumps({
        "device_family": profile.get("device_family", "unknown"),
        "platform": profile.get("platform", "unknown"),
        "model": profile.get("model", "unknown"),
        "boot_state": profile.get("boot_state", "unknown"),
        "compatibility_score": score,
        "recommended_action": action,
    }, indent=2))


if __name__ == "__main__":
    main()
