# Experimental data attribution

Wiezcorek, Alexander; Rodkey, Nathan; Sommerhauser, Jan; Hattrick-Simpers, Jason; Siol, Sebastian (2026). *Raw Data pertaining to publication of Autonomous Sampling and SHAP Interpretation of Bipolar HiPIMS Deposition Rates*. Zenodo, version 1. https://doi.org/10.5281/zenodo.18495402

License: Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/.

This project redistributes a transformed **Al 120 W** subset (601 measurements): safely extracted numeric literals from Campaign.json, deposition rate multiplied by 1000 × 1.1684, controls rounded to 8 decimal places for recipe identity, stable local recipe IDs added, duplicate-group mean aggregation implemented (no duplicates present). No original measurement was excluded by the finite, declared-bound or pulse-timing checks. This transformation and the new decision software are independent work; no author endorsement is implied.

Calibration is from the same archive's `Clean Datasets Used for Publication/Al - 120 W  - short PW/calibration.txt` (`220, 1.1684`). Factor 1000 converts raw kÅ/s to Å/s; material-density factor 1.1684 follows the authors' [documented preprocessing](https://github.com/bbfng/Autonomous-Sampling-and-SHAP-Interpretation-of-Deposition-Rate-in-Bipolar-HiPIMS/blob/main/src/hipims_bo_utils.py). The first field, 220, is an oscilloscope sampling window and is not a rate multiplier.

Source SHA-256 and bounds are in audit.json. `scripts/prepare_data.py` uses pickletools to inspect literal numeric byte buffers. It never invokes pickle.load, pickle.loads or arbitrary serialized callables. This narrow decoder intentionally rejects other dataframe layouts. No author source code was copied into this implementation.
