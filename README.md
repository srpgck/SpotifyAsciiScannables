# SpotifyAsciiScannables

A command-line tool written in Python that converts Spotify URLs or URIs into scannable ASCII art Spotify Codes. It also retrieves and displays track metadata directly in the terminal using Spotify's oEmbed API.

---

## Features

- **Four Adjustable Sizes**: Render codes in `tiny`, `small`, `medium`, or `large` formats to fit different terminal sizes.
- **Metadata Resolution**: Automatically queries the Spotify oEmbed API to display the track title and details.
- **Flexible Input Support**: Accepts standard Spotify Web URLs (including internationalized links) as well as raw Spotify URIs.
- **Accurate Code Mapping**: Parses SVG heights obtained from the official Spotify Scannable endpoint and maps them into custom block-character heights for scanning readability.

---

## Prerequisites

This script requires Python 3.7+ and the `requests` library to communicate with Spotify's endpoints.

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/srpgck/SpotifyAsciiScannables.git
   cd SpotifyAsciiScannables
   ```

2. **Install Dependencies**
   Install the required `requests` library:
   ```bash
   pip install requests
   ```

---

## Usage

Run the program by passing a Spotify URL or URI as the primary argument.

```bash
python main.py <spotify_url_or_uri> [options]
```

### Options

| Flag | Name | Type | Description |
|---|---|---|---|
| `-h`, `--help` | Help | | Shows the built-in help menu and exit. |
| `-s`, `--size` | Size | string | Set code size: `tiny`, `small`, `medium`, `large` (Default: `medium`). |
| `-d`, `--debug`| Debug | | Enable debug logs for request troubleshooting. |

---

## Examples & Output Previews

You can preview the pre-rendered outputs for each size directly on GitHub by visiting the files in the [examples/](examples/) directory:

* 🔍 [**Large Size Example**](examples/large.md) *(Recommended for optimal camera scanning)*
* 🟢 [**Medium Size Example**](examples/medium.md) *(Default size)*
* ⚠️ [**Small Size Example**](examples/small.md) *(Not recommended for camera scanning)*
* ⚠️ [**Tiny Size Example**](examples/tiny.md) *(Not recommended for camera scanning)*

---

## Command Line Examples

$$\large\color{red}\textbf{Works best in medium and large (tiny and small are not suggested!!!)}$$

**Default (Medium size):**
```bash
python main.py "https://open.spotify.com/track/1DwscornXpj8fmOmYVlqZt"
```

**Large size using a raw URI:**
```bash
python main.py spotify:track:1DwscornXpj8fmOmYVlqZt -s large
```

**Tiny size with debug logs enabled:**
```bash
python main.py "https://open.spotify.com/track/1DwscornXpj8fmOmYVlqZt" -s tiny --debug
```

---

## Technical Overview

1. **Data Retrieval**: The script takes the input URL/URI, standardizes it into a Spotify URI, and fetches the official vector format (SVG) of the barcode from `scannables.scdn.co`.
2. **SVG Parsing**: Using regular expressions, the code extracts the height attributes of the 23 baseline bars.
3. **Level Mapping**: Height values are normalized and mapped into 8 levels (Base-8 height scaling) corresponding to predefined ASCII characters.
4. **Metadata lookup**: In parallel, the Spotify oEmbed API is used to fetch the resource title for context.

---

## License

```
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
