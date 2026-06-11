# Technical Specifications & Data Processing Details

This document provides a deep dive into the scientific methodology, mathematical algorithms, and implementation details of the Cosmic FITS Data Parser & RGB Image Visualizer.

---

## 🔭 Scientific Context

### Hubble Space Telescope (HST) WFC3/IR
The images analyzed in this project are captured by the **Wide Field Camera 3 (WFC3) Infrared Channel** on board the Hubble Space Telescope. 
- The detector is a $1024 \times 1024$ pixel Teledyne HgCdTe (Mercury-Cadmium-Telluride) focal plane array.
- WFC3/IR is highly sensitive to Near-Infrared (NIR) light, ranging from $800 \text{ nm}$ to $1700 \text{ nm}$.

### Medium-Band Infrared Filters
This pipeline processes observations from Proposal ID `15952` using three specific medium-band filters:
1. **F153M**: Central wavelength $\lambda_c \approx 1530 \text{ nm}$ (assigned to Red).
2. **F139M**: Central wavelength $\lambda_c \approx 1390 \text{ nm}$ (assigned to Green).
3. **F127M**: Central wavelength $\lambda_c \approx 1270 \text{ nm}$ (assigned to Blue).

These medium-band filters isolate specific spectroscopic windows in the NIR, allowing astronomers to resolve spatial features of gas clouds, dust lanes, and stellar populations while minimizing background sky noise.

---

## 📡 Data Retrieval: MAST Queries

The file [`download_hubble.py`](file:///f:/comsic_vizualization/download_hubble.py) utilizes `astroquery.mast` to query and download calibrated data.

### Query Logic
1. **Metadata Query**:
   `Observations.query_criteria` searches the database using criteria:
   - `proposal_id = "15952"`
   - `obs_collection = "HST"`
   - `filters = ["F127M", "F139M", "F153M"]`
2. **Calibrated Products Filtering**:
   Raw space-telescope exposures contain telemetry artifacts, cosmic rays, and detector defects. The pipeline filters products to only download **FLT** (Flat-fielded and calibrated) files:
   - `productSubGroupDescription="FLT"`
   - `extension="fits"`

---

## 🧮 Mathematical & Image Processing Pipeline

Astronomical FITS images possess high dynamic range (up to 16-32 bits per pixel) and contain physical units (typically electrons/second or Jansky flux units). Translating them to an 8-bit per channel RGB image requires strict mathematical conditioning:

### 1. Robust Normalization & Clipping
Raw exposures contain dead pixels, hot pixels, and cosmic ray strikes that manifest as extreme outliers. A simple minimum-maximum scaling would compress the visible galaxy structure into a narrow, dark range.
To solve this, the pipeline applies a percentile-based outlier rejection:

$$\text{vmin} = P_{0.5}(I)$$
$$\text{vmax} = P_{99.5}(I)$$

where $P_k(I)$ represents the $k$-th percentile of pixel intensities in image $I$.
The pixel intensities are then clipped to this range:

$$I_{\text{clipped}} = \max\left(\text{vmin}, \min\left(\text{vmax}, I\right)\right)$$

Finally, a linear min-max stretch scales the pixel values to the range $[0, 1]$ suitable for display:

$$I_{\text{normalized}} = \frac{I_{\text{clipped}} - \text{vmin}}{\text{vmax} - \text{vmin}}$$

### 2. Sub-Pixel Image Alignment (Registration)
Because the telescope undergoes tiny thermal drifts and guidance shifts between target exposures, images taken through different filters are slightly offset. The script [`rgb.py`](file:///f:/comsic_vizualization/first_example/rgb.py) aligns these channels using **Phase Cross-Correlation (PCC)** in the Fourier domain.

#### Phase Cross-Correlation Algorithm
Given a reference image $R(x, y)$ (Red channel) and a shifted target image $T(x, y)$ (Green or Blue channel), the Fourier shift theorem states that a spatial translation is equivalent to a phase shift in the frequency domain.

1. Compute the 2D Discrete Fourier Transforms (DFTs):
   $$\mathcal{F}_R(u, v) = \text{FFT2D}(R)$$
   $$\mathcal{F}_T(u, v) = \text{FFT2D}(T)$$

2. Compute the cross-power spectrum:
   $$C(u, v) = \frac{\mathcal{F}_R(u, v) \cdot \mathcal{F}_T^*(u, v)}{\left| \mathcal{F}_R(u, v) \cdot \mathcal{F}_T^*(u, v) \right|}$$
   where $\mathcal{F}_T^*(u, v)$ is the complex conjugate of $\mathcal{F}_T(u, v)$.

3. Compute the Inverse Fourier Transform of the cross-power spectrum (the phase correlation):
   $$cc(x, y) = \text{IFFT2D}(C)$$

4. Find the location of the peak in $cc(x, y)$:
   $$(\Delta x, \Delta y) = \arg\max_{x, y} \left( cc(x, y) \right)$$

This peak location gives the integer translation offset. `scikit-image`'s `phase_cross_correlation` extends this to achieve **sub-pixel accuracy** using matrix-multiply DFT upsampling, measuring translations down to fractions of a pixel (e.g., $0.01$ pixels).

#### Applying the Shift
The target image is shifted back using `scipy.ndimage.shift`, which uses spline interpolation to shift the pixel grid by non-integer offsets:

$$T_{\text{aligned}}(x, y) = \text{Interpolate}\left( T(x - \Delta x, y - \Delta y) \right)$$

---

## 💻 Code Architecture Walkthrough

### 1. `download_hubble.py`
- **Purpose**: Automates data acquisition.
- **Key Method**: `Observations.download_products()` downloads target FITS files and maintains a structured directory scheme in [`hubble_data/`](file:///f:/comsic_vizualization/hubble_data).

### 2. `first_example/rgb.py`
- **Purpose**: Demonstate single-pointing alignment and RGB rendering.
- **Sequence**:
  1. Calls `load_and_normalize()` on Red, Green, and Blue bands.
  2. Compares Green to Red, and Blue to Red, returning translation vectors.
  3. Translates Green and Blue channels using `shift()`.
  4. Stacks them into a 3D NumPy array: `np.dstack((red, green_aligned, blue_aligned))`.
  5. Clips values to `[0, 1]` to ensure proper plotting.
  6. Saves as `andromeda_ir_rgb_aligned.png` using $300 \text{ DPI}$ scaling.

### 3. `first_example/gen_all.py`
- **Purpose**: Batch-process all downloaded HST image sets.
- **Workflow**:
  - Traverses the downloaded directory looking for FITS files ending in `_flt.fits`.
  - Automatically parses filename strings to sort files into three lists: `f127_files`, `f139_files`, and `f153_files`.
  - Pairs them using `zip(f153_files, f139_files, f127_files)` (mapping longest to shortest wavelengths).
  - Processes each group to save `auto_rgb_xxx.png`.

> [!CAUTION]
> **Important Bug in `first_example/gen_all.py`**:
> Line 52 of [`gen_all.py`](file:///f:/comsic_vizualization/first_example/gen_all.py) contains a hardcoded reference to a directory that does not exist on your machine:
> ```python
> base_path = r"F:\comsic_classifier\hubble_data\mastDownload\HST"
> ```
> To run the script successfully, this must be updated to the actual workspace download directory:
> ```python
> base_path = r"F:\comsic_vizualization\hubble_data\mastDownload\HST"
> ```
