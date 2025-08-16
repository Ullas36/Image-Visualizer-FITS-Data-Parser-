from astroquery.mast import Observations
import os

proposal_id = "15952"
filters = ["F127M", "F139M", "F153M"]

# 1. Search for HST data under the proposal ID with your filters
obs = Observations.query_criteria(proposal_id=proposal_id, obs_collection="HST", filters=filters)

# 🧠 Check what columns we DO have
print("🔍 Available columns:\n", obs.colnames)

# 🔎 You can preview results before downloading
print("\n🔬 Preview matching rows:")
print(obs[["obs_id", "filters", "instrument_name", "target_name"]][:5])

# 2. Get products (actual files) associated with those observations
products = Observations.get_product_list(obs)

# 3. Filter only the calibrated 'FLT' fits images
flt_files = Observations.filter_products(products,
    productSubGroupDescription="FLT",
    extension="fits"
)

# 4. Download to a clean directory
os.makedirs("hubble_data", exist_ok=True)
Observations.download_products(flt_files, download_dir="hubble_data")

print("\n✅ Done. Files downloaded into `hubble_data/` folder.")
