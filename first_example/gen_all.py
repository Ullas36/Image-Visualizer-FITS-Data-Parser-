import os
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

def load_and_normalize(path):
    data = fits.getdata(path)
    data = np.nan_to_num(data)
    vmin, vmax = np.percentile(data, (0.5, 99.5))
    data = np.clip(data, vmin, vmax)
    norm = (data - vmin) / (vmax - vmin)
    return norm

def build_rgb_image(r_path, g_path, b_path, output_path):
    red   = load_and_normalize(r_path)
    green = load_and_normalize(g_path)
    blue  = load_and_normalize(b_path)

    rgb = np.dstack((red, green, blue))
    rgb = np.clip(rgb, 0, 1)

    plt.figure(figsize=(10, 10))
    plt.imshow(rgb, origin='lower')
    plt.title("Auto RGB Composite")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def find_rgb_groups(base_folder):
    f127_files, f139_files, f153_files = [], [], []

    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith("_flt.fits"):
                lower = file.lower()
                full_path = os.path.join(root, file)
                if "f127" in lower:
                    f127_files.append(full_path)
                elif "f139" in lower:
                    f139_files.append(full_path)
                elif "f153" in lower:
                    f153_files.append(full_path)

    print(f"[DEBUG] F127: {len(f127_files)} | F139: {len(f139_files)} | F153: {len(f153_files)}")
    
    # Combine available groups (limited to shortest set)
    groups = list(zip(f153_files, f139_files, f127_files))  # R, G, B
    return groups

# Main run
base_path = r"F:\comsic_classifier\hubble_data\mastDownload\HST"
rgb_groups = find_rgb_groups(base_path)
print(f"[INFO] Total RGB groups found: {len(rgb_groups)}")

for i, (r, g, b) in enumerate(rgb_groups[:10]): 
    print(f"[INFO] Generating image {i + 1}/{len(rgb_groups)}")
    out_file = f"auto_rgb_{i+1:03}.png"
    build_rgb_image(r, g, b, out_file)
