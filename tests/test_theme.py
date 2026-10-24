"""Theme-Tests: Dark/Light-Parität und WCAG-Kontrast per Rechnung (kein Browser nötig)."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from validate import load_yaml  # noqa: E402

THEME = load_yaml(REPO_ROOT / "themes" / "magguu_midnight.yaml")["Magguu Midnight"]["modes"]


def parse_color(value: str) -> tuple[float, float, float, float]:
    value = value.strip()
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        r, g, b = (int(digits[i : i + 2], 16) for i in (0, 2, 4))
        return r, g, b, 1.0
    match = re.fullmatch(r"rgba?\(([^)]*)\)", value)
    assert match, f"unbekannte Farbe: {value}"
    parts = [float(p) for p in match.group(1).split(",")]
    return parts[0], parts[1], parts[2], parts[3] if len(parts) == 4 else 1.0


def over(fg: tuple[float, float, float, float], bg: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    a = fg[3]
    return (*(fg[i] * a + bg[i] * (1 - a) for i in range(3)), 1.0)


def luminance(color: tuple[float, float, float, float]) -> float:
    def channel(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in color[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: tuple[float, float, float, float], bg: tuple[float, float, float, float]) -> float:
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def page_background(mode: str) -> tuple[float, float, float, float]:
    return parse_color(THEME[mode]["primary-background-color"])


def surface(mode: str) -> tuple[float, float, float, float]:
    """mag-surface liegt (teiltransparent) auf dem Seitenhintergrund."""
    return over(parse_color(THEME[mode]["mag-surface"]), page_background(mode))


class ThemeTest(unittest.TestCase):
    def test_dark_and_light_define_the_same_variables(self) -> None:
        self.assertEqual(sorted(THEME["dark"]), sorted(THEME["light"]))

    def test_contrast_helper_matches_known_wcag_values(self) -> None:
        black, white = (0, 0, 0, 1.0), (255, 255, 255, 1.0)
        self.assertAlmostEqual(contrast(black, white), 21.0, places=1)
        self.assertAlmostEqual(contrast((119, 119, 119, 1.0), white), 4.48, places=1)

    def test_text_meets_wcag_aa_on_page_and_card_in_both_modes(self) -> None:
        for mode in ("dark", "light"):
            for name in ("mag-text", "primary-text-color", "mag-text-muted", "secondary-text-color"):
                fg = parse_color(THEME[mode][name])
                for label, bg in (("Seite", page_background(mode)), ("Karte", surface(mode)),
                                  ("Kartenhintergrund", over(parse_color(THEME[mode]["ha-card-background"]), page_background(mode)))):
                    self.assertGreaterEqual(contrast(fg, bg), 4.5, f"{mode}: {name} auf {label} = {contrast(fg, bg):.2f}")

    def test_accent_colors_are_readable_on_the_card_surface_in_both_modes(self) -> None:
        for mode in ("dark", "light"):
            for name in [n for n in THEME[mode] if n.startswith("mag-accent-")]:
                ratio = contrast(parse_color(THEME[mode][name]), surface(mode))
                self.assertGreaterEqual(ratio, 4.5, f"{mode}: {name} = {ratio:.2f}")

    def test_room_accent_hex_values_stay_readable_after_the_light_mode_mix(self) -> None:
        """Kartenakzente sind Hex-Werte (z. B. #ffd166 = 1,5:1 auf Weiß); im Hellmodus mischt das Theme sie zum Text-Ton."""
        used = set()
        for path in (REPO_ROOT / "dashboard").rglob("*.yaml"):
            used |= {m.lower() for m in re.findall(r"accent: *'(#[0-9a-fA-F]{6})'", path.read_text(encoding="utf-8"))}
        self.assertGreaterEqual(len(used), 10)
        for mode in ("dark", "light"):
            strength = float(THEME[mode]["mag-room-accent-strength"].rstrip("%")) / 100
            ink = parse_color(THEME[mode]["mag-room-accent-ink"])
            for hex_value in sorted(used):
                base = parse_color(hex_value)
                mixed = tuple(strength * b + (1 - strength) * i for b, i in zip(base[:3], ink[:3])) + (1.0,)
                for label, bg in (("Karte", surface(mode)), ("Seite", page_background(mode))):
                    ratio = contrast(mixed, bg)
                    self.assertGreaterEqual(ratio, 4.5, f"{mode}: {hex_value} auf {label} = {ratio:.2f}")

    def test_room_accent_foregrounds_always_go_through_the_theme_mix(self) -> None:
        text = (REPO_ROOT / "dashboard" / "magguu-dashboard" / "shared" / "templates" / "button_card.yaml").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"color: '\[\[\[ return variables\.accent")
        self.assertGreaterEqual(text.count("--mag-room-accent-strength"), 4)

    def test_weather_tile_in_the_hero_is_as_light_as_the_cards_in_light_mode(self) -> None:
        """6.8.0-dev live: Overlay-Grau wirkte neben weißen Karten fremd; Text bleibt darauf lesbar."""
        for mode in ("dark", "light"):
            tile = over(parse_color(THEME[mode]["mag-weather-surface"]), surface(mode))
            for name in ("primary-text-color", "secondary-text-color"):
                self.assertGreaterEqual(contrast(parse_color(THEME[mode][name]), tile), 4.5, f"{mode}: {name}")
        light_tile = over(parse_color(THEME["light"]["mag-weather-surface"]), page_background("light"))
        self.assertGreater(luminance(light_tile), 0.85)

    def test_state_and_primary_colors_reach_non_text_contrast_in_both_modes(self) -> None:
        for mode in ("dark", "light"):
            for name in ("primary-color", "state-light-active-color", "state-cover-active-color", "state-climate-heat-color"):
                ratio = contrast(parse_color(THEME[mode][name]), surface(mode))
                self.assertGreaterEqual(ratio, 3.0, f"{mode}: {name} = {ratio:.2f}")

    def test_light_mode_is_really_light_and_dark_mode_is_still_dark(self) -> None:
        self.assertGreater(luminance(page_background("light")), 0.8)
        self.assertGreater(luminance(surface("light")), 0.8)
        self.assertLess(luminance(page_background("dark")), 0.02)
        self.assertLess(luminance(surface("dark")), 0.02)


if __name__ == "__main__":
    unittest.main()
