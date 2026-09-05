"""Spot-check audio synthesis across all 12 Indian languages in config.LANGUAGES.

Ensures that:
1. Every voice / language key synthesizes a valid MP3 file > 1000 bytes.
2. No language fails or produces silent placeholders.
"""
import sys
from pathlib import Path

# Windows consoles default to cp1252 and cannot print Indic scripts.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from src.tts import synthesize

PHRASES = {
    "English": "Welcome to BharatGuru, your adaptive AI teacher.",
    "Hindi": "भारतगुरु में आपका स्वागत है, आपकी व्यक्तिगत एआई शिक्षा।",
    "Hinglish": "BharatGuru me aapka swagat hai, aaj hum physics seekhenge.",
    "Tamil": "பாரத்குருவுக்கு நல்வரவு, உங்கள் தனிப்பயனாக்கப்பட்ட ஆசிரியர்.",
    "Telugu": "భారత్‌గురుకి స్వాగతం, మీ వ్యక్తిగత ఏఐ ఉపాధ్యాయుడు.",
    "Kannada": "ಭಾರತ್‌ಗುರುಗೆ ಸುಸ್ವಾಗತ, ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಶಿಕ್ಷಕ.",
    "Malayalam": "ഭാരത്ഗുരുവിലേക്ക് സ്വാഗതം, നിങ്ങളുടെ പഠന സഹായി.",
    "Bengali": "ভারতগুরুতে স্বাগতম, আপনার ব্যক্তিগত শিক্ষক।",
    "Marathi": "भारतगुरु मध्ये आपले स्वागत आहे, तुमचे वैयक्तिक शिक्षक.",
    "Gujarati": "ભારતગુરુમાં આપનું સ્વાગત છે, આપના વ્યક્તિગત શિક્ષક.",
    "Punjabi": "ਭਾਰਤਗੁਰੂ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ, ਤੁਹਾਡਾ ਨਿੱਜੀ ਅਧਿਆਪਕ।",
    "Urdu": "بھارت گرو میں خوش آمدید، آپ کے ذاتی استاد۔",
}

def main():
    test_dir = config.WORKDIR / "lang_test_audio"
    test_dir.mkdir(parents=True, exist_ok=True)
    print(f"Testing TTS synthesis across all {len(config.LANGUAGES)} languages...\n")

    results = {}
    for lang, info in config.LANGUAGES.items():
        text = PHRASES.get(lang, "Welcome to BharatGuru.")
        out_file = test_dir / f"test_{lang}.mp3"
        out_file.unlink(missing_ok=True)
        try:
            res_path = synthesize(text, lang, out_file)
            size = res_path.stat().st_size if res_path.exists() else 0
            success = size > 1000
            results[lang] = {"success": success, "size": size, "voice": info["voice"]}
            status = "PASS" if success else "FAIL"
            print(f"  [{status}] {lang:12} ({info['native']}): {size:,} bytes | Voice: {info['voice']}")
        except Exception as exc:
            results[lang] = {"success": False, "error": str(exc)}
            print(f"  [FAIL] {lang:12}: Exception {exc}")

    failed = [k for k, v in results.items() if not v.get("success")]
    if failed:
        print(f"\nFAILED LANGUAGES: {failed}")
        sys.exit(1)
    else:
        print(f"\nALL {len(config.LANGUAGES)} LANGUAGES PASSED AUDIO SYNTHESIS!")

if __name__ == "__main__":
    main()
