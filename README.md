# landsat8_QAmask

A function that uses GDAL to mask out any combination of criteria from a LANDSAT8 QA band image

I've seen a few scripts out there that read the landsat8 QA band and mask out undesirable stuff,  but I was dissatisfied with how rigid they were.  There's a boatload of information packed into those tiny little int16s: http://landsat.usgs.gov/qualityband.php

This script lets you specify a list of criteria that you want to make a mask from, and you can specify any combination of them.  Just remember that you are telling the script what to REMOVE From the image.  So entering 'CLOUD_YES' into the criteria list will REMOVE anything that meets the 'CLOUD_YES' criterion.

Shoutout to Oren Tirosh from http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/ for writing a lightning-fast memoizer decorator function.  Without it implemented here, processing one image with one criterion took 6 minutes.  With it, it took 50 seconds.

You'll have to supply your own landsat images to run the demo, since they're too big for github.

# How to use it:

Look in landsat8_QAmask_demo.py

# Parameter list:

in_qa_band (GDAL Band object): A GDAL band object made from your LANDSAT 8 QA band image.

in_criteria_list (list): A list of criteria that you want to EXCLUDE in your mask.  Valid list of criteria is included at the end of this doc.

in_rows (int): Number of rows in your image.

in_cols (int): Number of cols in your image.

in_geotransform (GDAL Geotransform object): Geographic transformation

out_tiff (string) (output): Output tiff to be created.  It will consist entirely of 1s and 0s so you can multiply it with any other image from the set.  You should probably make sure it ends with '.tif', but you're the boss, man.

# Valid criteria:

Put any combination of these strings in a list and input it as the 'in_criteria_list' parameter:

'CLOUD_NOTDETERMINED'

'CLOUD_NO'

'CLOUD_MAYBE'

'CLOUD_YES'

'CIRRUS_NOTDETERMINED'

'CIRRUS_NO'

'CIRRUS_MAYBE'

'CIRRUS_YES'

'SNOWICE_NOTDETERMINED'

'SNOWICE_NO'

'SNOWICE_MAYBE'

'SNOWICE_YES'

'VEGETATION_NOTDETERMINED'

'VEGETATION_NO'

'VEGETATION_MAYBE'

'VEGETATION_YES'

'CLOUDSHADOW_NOTDETERMINED'

'CLOUDSHADOW_NO'

'CLOUDSHADOW_MAYBE'

'CLOUDSHADOW_YES'

'WATER_NOTDETERMINED'

'WATER_NO'

'WATER_MAYBE'

'WATER_YES'

'RESERVED_NO'

'RESERVED_YES'

'TERRAINOCCLUSION_NO'

'TERRAINOCCLUSION_YES'

'DROPPEDFRAME_NO'

'TERRAINOCCLUSION_YES'

'DESIGNATEDFILL_NO'

'DESIGNATEDFILL_YES'
