import argparse
import json
from datetime import datetime
from pathlib import Path


class HardwareProfile:
    def __init__(self, data):
        self.data = data

    def platform(self):
        return self.data.get("platform", "unknown")

    def __getitem__(self, key):
        return self.data.get(key)


class RWXAIEngine:
    PLATFORM_RULES = {
        "xbox": {"recovery": 0.95, "normal": 0.90, "fault": 0.65},
        "playstation": {"recovery": 0.95, "normal": 0.90, "fault": 0.60},
        "nintendo": {"recovery": 0.90, "normal": 0.85, "fault": 0.55},
        "pc": {"recovery": 0.80, "normal": 0.75, "fault": 0.50},
        "console": {"recovery": 0.95, "normal": 0.90, "fault": 0.65},
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

    def _normalize_platform(self, profile):
        platform = str(profile.get("platform", "pc")).strip().lower()
        brand = str(profile.get("brand", "")).strip().lower()
        for source in (brand, platform):
            if not source:
                continue
            resolved = self.PLATFORM_ALIASES.get(source)
            if resolved:
                return resolved
        return platform or "pc"

    def analyze_profile(self, profile):
        platform = self._normalize_platform(profile)
        boot_state = str(profile.get("boot_state", "unknown")).lower()
        base_score = self.PLATFORM_RULES.get(platform, self.PLATFORM_RULES["pc"]).get(boot_state, 0.5)

        bonus = 0.0
        if profile.get("cpu"):
            bonus += 0.02
        if profile.get("gpu"):
            bonus += 0.02
        if profile.get("storage_gb"):
            bonus += 0.01
        if profile.get("ram_gb"):
            bonus += 0.01

        final_score = min(base_score + bonus, 1.0)
        recommendation = self._recommend(final_score)
        return {
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "model": profile.get("model", "unknown"),
            "boot_state": boot_state,
            "compatibility_score": round(final_score, 3),
            "risk_level": self._risk_level(final_score),
            "recommended_action": recommendation,
        }

    def _recommend(self, score):
        if score >= 0.90:
            return "Load approved recovery image and continue diagnostics."
        if score >= 0.75:
            return "Inspect hardware metadata and verify device state before loading any recovery image."
        return "Stop and validate the target hardware before attempting recovery."

    def _risk_level(self, score):
        if score >= 0.90:
            return "Low Risk"
        if score >= 0.75:
            return "Medium Risk"
        if score >= 0.60:
            return "High Risk"
        return "Critical Risk"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a hardware profile")
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()

    with Path(args.profile).open("r", encoding="utf-8") as f:
        profile = json.load(f)

    engine = RWXAIEngine()
    print(json.dumps(engine.analyze_profile(profile), indent=2))
