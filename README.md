# nci-assert-values-greater-than-baseline
NCI - assert values for all scenarios greater than what's in the restoration scenario

# How to Read the Outputs

Given 2 rasters, "restoration" and "other",

* Pixel values of `1` indicate that `restoration >= other`
* Pixel values of `0` indicate that `restoration < other`
* Pixel values of `255` indicate that either `restoration` or `other` were
  nodata.

