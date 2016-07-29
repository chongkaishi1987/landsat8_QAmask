import gdal
import numpy as np
from numpy import nditer, binary_repr, ones
from gdal import GetDriverByName

# Master dict that maps all criteria to their start/end bits and their values.
CRITERIA_DICT = {      'CLOUD_NOTDETERMINED': (0, 2, '00'),
                                  'CLOUD_NO': (0, 2, '01'),
                               'CLOUD_MAYBE': (0, 2, '10'),
                                 'CLOUD_YES': (0, 2, '11'),
                      'CIRRUS_NOTDETERMINED': (2, 4, '00'),
                                 'CIRRUS_NO': (2, 4, '01'),
                              'CIRRUS_MAYBE': (2, 4, '10'),
                                'CIRRUS_YES': (2, 4, '11'),
                     'SNOWICE_NOTDETERMINED': (4, 6, '00'),
                                'SNOWICE_NO': (4, 6, '01'),
                             'SNOWICE_MAYBE': (4, 6, '10'),
                               'SNOWICE_YES': (4, 6, '11'),
                  'VEGETATION_NOTDETERMINED': (6, 8, '00'),
                             'VEGETATION_NO': (6, 8, '01'),
                          'VEGETATION_MAYBE': (6, 8, '10'),
                            'VEGETATION_YES': (6, 8, '11'),
                 'CLOUDSHADOW_NOTDETERMINED': (8, 10, '00'),
                            'CLOUDSHADOW_NO': (8, 10, '01'),
                         'CLOUDSHADOW_MAYBE': (8, 10, '10'),
                           'CLOUDSHADOW_YES': (8, 10, '11'),
                       'WATER_NOTDETERMINED': (10, 12, '00'),
                                  'WATER_NO': (10, 12, '01'),
                               'WATER_MAYBE': (10, 12, '10'),
                                 'WATER_YES': (10, 12, '11'),
                               'RESERVED_NO': (12, 13, '00'),
                              'RESERVED_YES': (12, 13, '01'),
                       'TERRAINOCCLUSION_NO': (13, 14, '10'),
                      'TERRAINOCCLUSION_YES': (13, 14, '11'),
                           'DROPPEDFRAME_NO': (14, 15, '10'),
                      'TERRAINOCCLUSION_YES': (14, 15, '11'),
                         'DESIGNATEDFILL_NO': (14, 15, '10'),
                        'DESIGNATEDFILL_YES': (14, 15, '11')
                 }

def memodict(f):

    # Memoization decorator for a function taking a single argument
    # This increases speed by factor of TEN.  LUDICROUS SPEED! GO!
    # http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/

    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


@memodict
def check_criteria(in_tuple):

    # Read the input int (first item in input_tuple) as a string and check the sliced out portion as indicated in the
    # criterion (second item in input_tuple).  This line is very computationally expensive and is alleviated by the
    # memodict decorator - it will only be called if a shortcut from the input int directly to the answer doesn't
    # already exist in memodict.

    for criterion in in_tuple[1].split(','):
        if binary_repr(in_tuple[0], 16)[CRITERIA_DICT[criterion][0]:CRITERIA_DICT[criterion][1]] == CRITERIA_DICT[criterion][2]:
            return True
        else:
            return False


def qa_mask(in_qa_band, in_criteria_list, in_rows, in_cols, in_geotransform, out_tiff):

    # This function takes in a LANDSAT8 QA band (or a clipped out piece of one), and analyzes every pixel to mask out
    # whatever you want based on input criteria.  Remember that the criteria you supply in in_criteria_list are things
    # you want EXCLUDED from the image.  So if you want to get rid of clouds, put 'CLOUD_YES' in in_criteria_list,
    # so that any pixel in the output mask that has the 'CLOUD_YES' criterion is set to 0.

    # Copy the QA band to a numpy array and make a new array of all 1's with the same dimensions.
    np_qa = in_qa_band.ReadAsArray(0, 0, in_cols, in_rows)
    np_mask = ones((in_rows, in_cols), dtype=np.int16)

    # Iterate through every pixel
    it = nditer(np_qa, flags=['multi_index'])

    while not it.finished:

        row = it.multi_index[0] # y position in array
        col = it.multi_index[1] # x position in array

        # Call check_criteria on the pixel.  You have to pass it the entire criteria list each time but it's always the
        # same so it shouldn't affect the memoizer.

        # apparently the function doesn't like taking a tuple with a list as one of its elements.
        # TypeError: unhashable type 'list'?????
        if check_criteria((np_qa[row, col], ','.join(in_criteria_list))):
            np_mask[row, col] = 0

        it.iternext()

    # Make a driver
    geotiff = GetDriverByName('GTiff')

    # Make a new tiff and dump the contents of the masked numpy array into it.
    output = geotiff.Create(out_tiff, in_cols, in_rows, 1, gdal.GDT_Int16)
    output_band = output.GetRasterBand(1)
    output_band.WriteArray(np_mask)
    output.SetGeoTransform(in_geotransform)

    return None