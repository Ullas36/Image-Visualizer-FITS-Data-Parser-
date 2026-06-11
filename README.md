# Cosmic FITS Data Parser & RGB Image Visualizer

An automated pipeline to search, download, align, and generate multi-band Near-Infrared (NIR) RGB composite images from Hubble Space Telescope (HST) FITS observations.

---

## 🌌 Project Overview

This repository provides tools for astronomical image processing using Python. Specifically, it interfaces with the Space Telescope Science Institute (STScI) **MAST (Mikulski Archive for Space Telescopes)** database to query and download calibrated Flat-Field (`_flt.fits`) images from Hubble's **Wide Field Camera 3 (WFC3) Infrared channel**. It then automatically aligns these multi-wavelength images (accounting for sub-pixel spacecraft drift) and stacks them into high-fidelity color-composite PNG images.

---

## 📁 Repository Structure

*   **[`download_hubble.py`](file:///f:/comsic_vizualization/download_hubble.py)**: A script that queries MAST for a specific HST Proposal ID (`15952`) and filter set, retrieves observation products, filters for calibrated `FLT` FITS files, and downloads them.
*   **[`hubble_data/`](file:///f:/comsic_vizualization/hubble_data)**: The target download directory for raw Hubble FITS data.
*   **[`first_example/`](file:///f:/comsic_vizualization/first_example)**: A workspace folder containing demo scripts, input FITS files, and processed output images:
    *   **[`rgb.py`](file:///f:/comsic_vizualization/first_example/rgb.py)**: Performs sub-pixel image alignment (registration) using Fourier-domain cross-correlation to align different bands, stacks them into a Red-Green-Blue (RGB) matrix, and saves the final composite image of Andromeda.
    *   **[`gen_all.py`](file:///f:/comsic_vizualization/first_example/gen_all.py)**: Automatically matches, groups, and batch-processes downloaded FITS images into corresponding RGB composite frames.
    *   **`*.fits`**: Calibrated multi-band FITS frames of Andromeda (`ie3505ioq_flt.fits`, `ie3505iuq_flt.fits`, `ie3506joq_flt.fits`, `f127_flt.fits`, `f138_flt.fits`, `f153_flt.fits`).
    *   **`andromeda_ir_rgb_aligned.png`**: The final high-quality aligned infrared composite image.
    *   **`auto_rgb_001.png` - `auto_rgb_010.png`**: Batch-processed RGB composite images.

---

## 🛠️ Installation & Setup

Ensure you have Python 3.8+ installed along with the required scientific libraries:

```bash
pip install numpy matplotlib astropy astroquery scikit-image scipy
```

> [!NOTE]
> `astroquery` is used to query the MAST database. `astropy` is used to parse the FITS headers and pixel tables. `scikit-image` and `scipy` perform the Fourier-domain phase cross-correlation alignment.

---

## 🚀 How to Run

### Step 1: Download HST Data
Run [`download_hubble.py`](file:///f:/comsic_vizualization/download_hubble.py) to fetch FITS files from the HST database:
```bash
python download_hubble.py
```
This queries Proposal ID `15952` for filters `F127M`, `F139M`, and `F153M`, and downloads calibrated `FLT` images into `hubble_data/`.

### Step 2: Generate Aligned Composite Demo (Andromeda)
Run [`rgb.py`](file:///f:/comsic_vizualization/first_example/rgb.py) inside the [`first_example/`](file:///f:/comsic_vizualization/first_example) directory:
```bash
cd first_example
python rgb.py
```
This script loads three FITS files corresponding to three filter bands, normalizes the intensity scaling, registers the green and blue channels to match the red channel using sub-pixel phase cross-correlation, and stacks them into `andromeda_ir_rgb_aligned.png`.

### Step 3: Batch Process Downloads
Run [`gen_all.py`](file:///f:/comsic_vizualization/first_example/gen_all.py) to automatically group and visualize all downloaded data:
```bash
python gen_all.py
```

> [!WARNING]
> **Configuration Path Warning:** In [`gen_all.py`](file:///f:/comsic_vizualization/first_example/gen_all.py), the base path is hardcoded as `F:\comsic_classifier\hubble_data\mastDownload\HST`. You will need to edit line 52 to point to your local directory (e.g., `F:\comsic_vizualization\hubble_data\mastDownload\HST` or a relative path) for it to find the downloaded files.

---

## 🎨 Wavelength-to-Color Mapping

The pipeline translates the invisible infrared wavelengths captured by Hubble into visible colors:

| Filter | Central Wavelength | Bandwidth Description | Assigned Color Channel |
| :--- | :--- | :--- | :--- |
| **`F153M`** | $1530 \text{ nm}$ | Medium-band Infrared (longest wavelength) | **Red Channel** |
| **`F139M`** | $1390 \text{ nm}$ | Medium-band Infrared (mid wavelength) | **Green Channel** |
| **`F127M`** | $1270 \text{ nm}$ | Medium-band Infrared (shortest wavelength) | **Blue Channel** |

---

## 📘 Documentation & Technical Details

For a deep dive into the underlying physics, mathematics, and algorithms used (including data normalization, sub-pixel phase registration, and image stacking), see the **[DETAILS.md](file:///f:/comsic_vizualization/DETAILS.md)** file.
