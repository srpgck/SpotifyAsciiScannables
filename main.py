import re
import argparse
import os
import sys
from datetime import datetime
from dataclasses import dataclass
from urllib.parse import quote, urlparse
import requests

class SpotifyCodeError(ValueError):
    """Exception class for Spotify URL and fetching errors."""

@dataclass(frozen=True)
class SpotifyResource:
    resource_type: str
    resource_id: str

    @property
    def uri(self) -> str:
        return f"spotify:{self.resource_type}:{self.resource_id}"

def parse_spotify_input(value: str) -> SpotifyResource:
    value = value.strip()
    if not value:
        raise SpotifyCodeError("Input cannot be empty.")

    if value.startswith("spotify:"):
        parts = value.split(":")
        return SpotifyResource(parts[1].lower(), parts[2].split("?")[0])

    parsed = urlparse(value)
    path_parts = [part for part in parsed.path.split("/") if part]
    if path_parts and path_parts[0].startswith("intl-"):
        path_parts = path_parts[1:]

    if len(path_parts) < 2:
        raise SpotifyCodeError("Invalid URL format.")

    return SpotifyResource(path_parts[0].lower(), path_parts[1].split("?")[0])

def build_code_url(spotify_input: str) -> str:
    spotify_uri = parse_spotify_input(spotify_input).uri
    encoded_uri = quote(spotify_uri, safe=":")
    return f"https://scannables.scdn.co/uri/plain/svg/000000/white/640/{encoded_uri}"

# ==========================================
# DESIGN CONFIGURATIONS
# ==========================================

# TINY (4 Rows) 

LOGO_TINY = [
    "  ▄██▄  ",
    " ██  ██ ",
    " ██  ██ ",
    "  ▀██▀  "
]
SHAPES_TINY = {
    0: [" ", "▄", " ", " "],
    1: [" ", "▄", "▀", " "],
    2: [" ", "▄", "█", " "],
    3: [" ", "█", "█", " "],
    4: [" ", "█", "█", "▀"],
    5: ["▄", "█", "█", "▀"],
    6: ["▄", "█", "█", "█"],
    7: ["█", "█", "█", "█"],
}

# SMALL (5 Rows)

LOGO_SMALL = [
    "   ▄██▄   ",
    "  ██  ██  ",
    "  ██- ██  ",
    "  ██  ██  ",
    "   ▀██▀   "
]
SHAPES_SMALL = {
    0: [" ", " ", "█", " ", " "],
    1: [" ", "▄", "█", " ", " "],
    2: [" ", "▄", "█", "▀", " "],
    3: [" ", "█", "█", "▀", " "],
    4: [" ", "█", "█", "█", " "],
    5: ["▄", "█", "█", "█", " "],
    6: ["▄", "█", "█", "█", "▀"],
    7: ["█", "█", "█", "█", "█"],
}

# MEDIUM (6 Rows)

LOGO_MEDIUM = [
    "   ▄██▄   ",
    " ▄██████▄ ",
    " ███▄▄███ ",
    " ███▀▀███ ",
    " ▀██████▀ ",
    "   ▀██▀   "
]
SHAPES_MEDIUM = {
    0: [" ", " ", "▄", "▀", " ", " "],
    1: [" ", " ", "▄", "█", " ", " "],
    2: [" ", "▄", "█", "█", " ", " "],
    3: [" ", "▄", "█", "█", "▀", " "],
    4: [" ", "█", "█", "█", "█", " "],
    5: ["▄", "█", "█", "█", "█", " "],
    6: ["▄", "█", "█", "█", "█", "█"],
    7: ["█", "█", "█", "█", "█", "█"],
}

# LARGE (8 Rows)

LOGO_LARGE = [
    "    ▄████▄    ",
    "  ▄████████▄  ",
    " ███ ▄▄▄▄ ███ ",
    " ██ ▀▀▀▀▀▀ ██ ",
    " ██▄  ▀▀  ▄██ ",
    " ███▄▄▄▄▄▄███ ",
    "  ▀████████▀  ",
    "    ▀████▀    "
]
SHAPES_LARGE = {
    0: [" ", " ", " ", "▄", "▀", " ", " ", " "],
    1: [" ", " ", " ", "█", "█", " ", " ", " "],
    2: [" ", " ", "▄", "█", "█", "▀", " ", " "],
    3: [" ", " ", "█", "█", "█", "█", " ", " "],
    4: [" ", "▄", "█", "█", "█", "█", "▀", " "],
    5: [" ", "█", "█", "█", "█", "█", "█", " "],
    6: ["▄", "█", "█", "█", "█", "█", "█", "▀"],
    7: ["█", "█", "█", "█", "█", "█", "█", "█"],
}

CONFIG = {
    "tiny": {"logo": LOGO_TINY, "shapes": SHAPES_TINY, "rows": 4, "bar_gap": " ", "logo_gap": " "},
    "small": {"logo": LOGO_SMALL, "shapes": SHAPES_SMALL, "rows": 5, "bar_gap": " ", "logo_gap": "  "},
    "medium": {"logo": LOGO_MEDIUM, "shapes": SHAPES_MEDIUM, "rows": 6, "bar_gap": " ", "logo_gap": "  "},
    "large": {"logo": LOGO_LARGE, "shapes": SHAPES_LARGE, "rows": 8, "bar_gap": "  ", "logo_gap": "   "},
}

def generate_ascii_code(spotify_input: str, size: str = "large") -> str:
    """
    Generates a perfectly scannable ASCII Spotify Code in the requested size.
    """
    if size not in CONFIG:
        raise ValueError("Size must be 'tiny', 'small', 'medium', or 'large'.")

    url = build_code_url(spotify_input)
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        svg_content = response.text
    except requests.RequestException as e:
        raise SpotifyCodeError(f"Could not reach Spotify Code API: {e}")

    # Extract all barcode bar heights from the SVG
    rect_pattern = re.compile(r'<rect[^>]+height="([\d.]+)"[^>]*>')
    heights_str = rect_pattern.findall(svg_content)

    if not heights_str:
        raise SpotifyCodeError("No barcode bars found in the SVG data.")

    heights = [float(h) for h in heights_str]

    # Filter out the underlying dummy bars and ensure we have exactly 23 bars
    if len(heights) >= 23:
        heights.remove(max(heights))
        bars = heights[-23:] 
    else:
        raise SpotifyCodeError("Not enough barcode data to generate standard code.")

    min_h = min(bars)
    max_h = max(bars)
    range_h = max_h - min_h if max_h > min_h else 1

    cfg = CONFIG[size]
    
    # Extract Base-8 structural heights
    bar_levels = []
    for h in bars:
        level_float = (h - min_h) / (range_h / 7)
        level = int(round(level_float))
        level = max(0, min(7, level))
        bar_levels.append(level)

    # Stitch the ascii block together line by line
    ascii_art = ""
    for r in range(cfg["rows"]):
        row_str = cfg["logo"][r] + cfg["logo_gap"] 
        row_str += cfg["bar_gap"].join([cfg["shapes"][level][r] for level in bar_levels])
        ascii_art += row_str + "\n"

    return ascii_art

# ==========================================
# OEMBED API FUNCTIONS
# ==========================================

def _get_request_url(spotify_url: str, debug: bool = False) -> str:
    base_url = "https://open.spotify.com/oembed?url="
    oembed_url = base_url + spotify_url
    result = oembed_url.replace(" ", "%20")
    if debug:
        print(f"Constructed oEmbed Request URL: {result}")
    return result

def _request_oembed(oembed_url: str, debug: bool = False) -> dict:
    response = requests.get(oembed_url)
    if response.status_code == 200:
        if debug:
            print(f"Successfully retrieved oEmbed data: {response.json()} from URL: {oembed_url}")
        return response.json()
    else:
        raise Exception(f"Failed to retrieve oEmbed data: {response.status_code} - {response.text}")

def get_oembed_data(spotify_url: str, debug: bool = False) -> dict:
    oembed_url = _get_request_url(spotify_url, debug)
    return _request_oembed(oembed_url, debug)

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    # Get the script name dynamically for the help menu
    script_name = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(
        prog="SpotifyAsciiGen",
        description=(
            "🎵 Generate beautifully formatted ASCII Spotify Codes.\n"
            "Retrieves and displays track metadata via the Spotify oEmbed API."
        ),
        epilog=(
            f"Examples:\n"
            f"  python {script_name} \"https://open.spotify.com/track/1DwscornXpj8fmOmYVlqZt\"\n"
            f"  python {script_name} spotify:track:1DwscornXpj8fmOmYVlqZt -s large\n"
            f"  python {script_name} \"https://open.spotify.com/track/1DwscornXpj8fmOmYVlqZt\" -s tiny --debug\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter # Ensure line breaks are displayed correctly
    )

    parser.add_argument(
        "spotify_url", 
        type=str, 
        help="The Spotify URL or URI to generate the ASCII code for."
    )
    
    parser.add_argument(
        "-s", "--size", 
        type=str, 
        default="medium", 
        choices=["tiny", "small", "medium", "large"],
        help="Size of the ASCII code.\nChoices: tiny, small, medium, large (default: medium)."
    )
    
    parser.add_argument(
        "-d", "--debug", 
        action="store_true", 
        help="Enable debug output for troubleshooting API calls."
    )

    # Show help menu if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    try:
        if args.debug:
            print("[*] Debug mode enabled. Fetching metadata...")

        # Fetch metadata using oEmbed API
        metadata = get_oembed_data(args.spotify_url, args.debug)
        track_title = metadata.get("title", "Unknown Title")
        
        # Generate a local timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display nicely formatted Stamp
        print("\n" + "═" * 56)
        print(f"  Title     : {track_title}")
        print(f"  Timestamp : {timestamp}")
        print(f"  Made by   : Sxrp")
        print("═" * 56 + "\n")

        size = args.size
        print(f"=== {size.upper()} SIZE ===")
        print(generate_ascii_code(args.spotify_url, size=size))
            
    except SpotifyCodeError as e:
        print(f"\n[!] Spotify Code Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] An unexpected error occurred: {e}", file=sys.stderr)
        if args.debug:
            raise e # Raise the exception to print the traceback in debug mode
        sys.exit(1)

if __name__ == "__main__":
    main()