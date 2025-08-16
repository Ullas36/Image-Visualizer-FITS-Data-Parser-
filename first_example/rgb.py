from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from skimage.registration import phase_cross_correlation
from scipy.ndimage import shift

# Load and normalize FITS image
def load_and_normalize(path):
    data = fits.getdata(path)
    data = np.nan_to_num(data)
    vmin, vmax = np.percentile(data, (0.5, 99.5))
    data = np.clip(data, vmin, vmax)
    norm = (data - vmin) / (vmax - vmin)
    return norm

# Load each filter
red = load_and_normalize("ie3505ioq_flt.fits")    # longest wavelength = red
green = load_and_normalize("ie3505iuq_flt.fits")
blue = load_and_normalize("ie3506joq_flt.fits")

# Align green and blue to red
shift_green, _, _ = phase_cross_correlation(red, green)
shift_blue, _, _ = phase_cross_correlation(red, blue)

green_aligned = shift(green, shift_green)
blue_aligned = shift(blue, shift_blue)

# Stack to RGB
rgb = np.dstack((red, green_aligned, blue_aligned))
rgb = np.clip(rgb, 0, 1)

# Plot
plt.figure(figsize=(10, 10))
plt.imshow(rgb, origin='lower')
plt.title("Andromeda - Aligned IR RGB Composite")
plt.axis('off')
plt.tight_layout()
plt.savefig("andromeda_ir_rgb_aligned.png", dpi=300)
plt.show()
