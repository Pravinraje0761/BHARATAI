"""Bharat Context Engine for BHARATGURU.

Grounds STEM and conceptual explanations in familiar Indian cultural,
geographical, and everyday real-world anchors.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

BHARAT_ANCHORS = {
    "baseball": "leather cricket ball bowled at 140 km/h",
    "baseballs": "cricket balls",
    "subway": "crowded Mumbai local train or AC Chennai Metro",
    "subways": "local trains or metro coaches",
    "snow": "heavy Western Ghats monsoon rainfall",
    "dollar": "Rupees (₹)",
    "dollars": "Rupees (₹)",
    "cents": "paise",
    "highway": "six-lane Golden Quadrilateral expressway",
    "supermarket": "local Kirana store / vegetable mandi",
    "football": "cricket or kabaddi",
    "lake": "village stepwell (Baori) or Dal Lake",
    "coffee": "hot roadside tapri Chai in a cutting glass",
    "space_agency": "ISRO's Chandrayaan-3 and PSLV launches",
    "bus": "red BEST bus or KSRTC state transport bus navigating a traffic turn",
}

REGIONAL_FLAVORS = {
    "Tamil": {
        "transport": "Chennai Metro / MRTS train",
        "landmark": "Marina Beach breeze / Nilgiris mountain tea estate",
        "sports": "CSK cricket match at Chepauk stadium / Kabaddi",
        "currency": "Rupees (₹)",
    },
    "Hindi": {
        "transport": "Delhi Metro Yellow Line / Varanasi Ghat boat",
        "landmark": "Yamuna expressway / Himalayan foothill streams",
        "sports": "Gully cricket on a Sunday afternoon / Dangal wrestling",
        "currency": "Rupees (₹)",
    },
    "Bengali": {
        "transport": "Kolkata Tram or Howrah Ferry across the Hooghly",
        "landmark": "Sundarbans delta / Darjeeling tea garden slope",
        "sports": "Eden Gardens cricket or football derby",
        "currency": "Rupees (₹)",
    },
    "Marathi": {
        "transport": "Mumbai Local Train / Pune PMPML bus",
        "landmark": "Sahyadri ghat road bends / Konkan coastal breeze",
        "sports": "Wankhede stadium match / Kho-Kho",
        "currency": "Rupees (₹)",
    },
    "Telugu": {
        "transport": "Hyderabad Metro / Godavari river bridge train",
        "landmark": "Araku valley / Charminar bustling market",
        "sports": "Gully cricket at Gymkhana grounds / Badminton",
        "currency": "Rupees (₹)",
    },
}


def get_bharat_context_prompt_directive(language: str = "English", preset_style: str = "") -> str:
    """Produces instructions for the LLM to inject Indian contextual metaphors."""
    flavor = REGIONAL_FLAVORS.get(language, REGIONAL_FLAVORS["Hindi"])

    directives = [
        "BHARAT CONTEXT DIRECTIVE:",
        "- Use authentic Indian everyday analogies: use cricket (bat impact, fast bowler, fielding), "
        f"{flavor['transport']}, {flavor['landmark']}, or local Indian household examples.",
        "- Never use baseball, American football, subways in US cities, or dollars ($).",
        "- All currency must be in Indian Rupees (₹).",
        "- If explaining forces, inertia, or momentum: draw parallels to a cricket batsman hitting a cover drive, "
        "a passenger bracing inside a braking state transport bus, or an ISRO rocket payload staging.",
    ]

    if "cricket" in preset_style.lower():
        directives.append(
            "- CRICKET FOCUS: Express every law and formula through cricket mechanics (e.g. Jasprit Bumrah's "
            "delivery speed, Rohit Sharma's bat swing momentum, catching a ball with soft hands)."
        )

    return "\n".join(directives)


import re

def indianize_text(text: str) -> str:
    """Post-processing filter to ensure Western tropes are replaced with Indian equivalents."""
    cleaned = text
    for western, indian in BHARAT_ANCHORS.items():
        cleaned = re.sub(rf"\b{re.escape(western)}\b", indian, cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("$", "₹")
    return cleaned
