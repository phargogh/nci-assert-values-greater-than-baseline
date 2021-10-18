# nci-assert-values-greater-than-baseline
NCI - assert values for all scenarios greater than what's in the restoration scenario

## Setup

1. Place all source scenario rasters into a directory, e.g. `./source_rasters`
   * All source rasters must have the prefix `noxn_in_drinking_water`
   * The raster `noxn_in_drinking_water_restoration.tif` must be present.
2. Install requirements. To do this with conda, run:
   ```
   conda create -y -p ./env -c conda-forge python=3.8 pygeoprocessing taskgraph
   ```
3. Run the script in the form `python compare.py <source dir> <target dir>`.
   For example:
   ```
   python compare.py ./source_rasters target_rasters
   ```

## How to Read the Outputs

Given 2 rasters, "restoration" and "other",

* Pixel values of `1` indicate that `restoration >= other`
* Pixel values of `0` indicate that `restoration < other`
* Pixel values of `255` indicate that either `restoration` or `other` were
  nodata.

Summary statistics for all rasters are written to `target_rasters/summary.txt`.

