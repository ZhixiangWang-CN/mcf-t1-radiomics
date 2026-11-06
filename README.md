# MCF T1 radiomics geometry audit

Code accompanying “Clarifying T1 radiomics feature availability in the MCF cohort”.

The paired comparison changes mask direction metadata after expert verification of image–mask voxel correspondence. Image and mask dimensions, spacing and origins must agree. Extraction uses label 1, binWidth 25, geometryTolerance 0.01, correctMask=True, normalize=False and default Original features, on native voxel grids.

## Recreate Figure 2

Install the plotting dependencies and run:

```sh
pip install -r requirements-plot.txt
python scripts/plot_geometry.py
python -m unittest discover -s tests
```

`data/geometry_comparison.csv` contains anonymized per-case measurements from the archived 3 October 2026 spatial audit. Figure 2 includes all 130 cases. Panel a is an empirical cumulative distribution; panel b shows exact case counts with circle areas and line widths proportional to counts. No smoothing or significance test is used. Outputs are editable PDF/SVG and 600 dpi PNG/TIFF.

Maximum excursion measures how far the ROI bounding box extends beyond the image support along any image axis, in mm. The support is [-0.5, size-0.5] in continuous-index coordinates. Containment is the percentage of foreground voxel centres inside that support, with a 1e-5 voxel tolerance. These are physical-space geometry measurements.

## Run paired extraction on locally available images

The original extraction environment was Python 3.10.16, PyRadiomics 3.0.1 and SimpleITK 2.5.0. Use Python 3.10 and install `requirements-extraction.txt`. Prepare a CSV manifest using `manifest.example.csv`; replace its example paths with local paths and record expert verification for each case.

```sh
python scripts/extract.py manifest.csv --out results
```

The command writes paired feature records and case-level geometry measurements. Foreground geometry uses positive mask labels, matching the archived spatial audit; radiomics extraction uses label 1. Raw image data and patient identifiers are not included. The portable extraction command was prepared from the archived workflow; the current revision rechecked stored results and did not rerun extraction on the original images.

## Contents and status

- `scripts/extract.py`: portable extraction and geometry calculations.
- `scripts/plot_geometry.py`: manuscript Figure 2.
- `data/geometry_comparison.csv`: Figure 2 source data.
- `tests/test_geometry.py`: synthetic geometry checks and source-data consistency.
- `figures/`: figure exports.

Repository: https://github.com/ZhixiangWang-CN/mcf-t1-radiomics
