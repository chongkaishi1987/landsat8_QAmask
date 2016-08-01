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
                          'DROPPEDFRAME_YES': (14, 15, '11'),
                         'DESIGNATEDFILL_NO': (15, 16, '10'),
                        'DESIGNATEDFILL_YES': (15, 16, '11')
                 }

def memodict(f):

    """
        Memoization decorator for check_criteria().  This is WAY faster than using lru_cache, even if it isn't quite as
        friendly.  Stores a cache of values tht is faster to search & access than to convert every int to string and
        slice out its bits.
        @param f check_criteria() function
        @type function
        @return Boolean
    """

    # This increases speed by factor of TEN.  LUDICROUS SPEED! GO!
    # http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/

    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


@memodict
def check_criteria(in_tuple):

    """
        Helper function for qa_mask().  Indicates if the pixel is to be masked out (set to 0) or not.
        @param in_tuple the first value is the integer to be evaluated, and the second value is a returned value from
               CRITERIA_DICT.
        @type tuple
        @return Boolean
    """

    for criterion in in_tuple[1].split(','):
        if binary_repr(in_tuple[0], 16)[CRITERIA_DICT[criterion][0]:CRITERIA_DICT[criterion][1]] == CRITERIA_DICT[criterion][2]:
            return True
    return False


def qa_mask(in_qa_band, in_criteria_list, in_rows, in_cols, in_geotransform, out_tiff):

    """
        Takes in a GDALRasterBand object of a LANDSAT-8 QA Band image and analyzes every pixel to mask out whatever you
        want excluded based on input criteria remember that the criteria you supply in in_criteria_list are things you
        want EXCLUDED from the image.  So if you want to get rid of clouds, put 'CLOUD_YES' in in_criteria_list, so that
        any pixel in the output mask that has the 'CLOUD_YES' criterion is set to 0.
        @param in_qa_band The LANDSAT-8 QA band image.
        @type in_qa_band GDALRasterBand object
        @param in_criteria_list A list of strings indicating which criteria you want to REMOVE from the image.  Valid
                                values are 'CLOUD_NOTDETERMINED', 'CLOUD_NO', 'CLOUD_MAYBE', 'CLOUD_YES',
                                'CIRRUS_NOTDETERMINED', 'CIRRUS_NO', 'CIRRUS_MAYBE', 'CIRRUS_YES',
                                'SNOWICE_NOTDETERMINED', 'SNOWICE_NO', 'SNOWICE_MAYBE', 'SNOWICE_YES',
                                'VEGETATION_NOTDETERMINED', 'VEGETATION_NO', 'VEGETATION_MAYBE', 'VEGETATION_YES',
                                'CLOUDSHADOW_NOTDETERMINED', 'CLOUDSHADOW_NO', 'CLOUDSHADOW_MAYBE', 'CLOUDSHADOW_YES',
                                'WATER_NOTDETERMINED', 'WATER_NO', 'WATER_MAYBE', 'WATER_YES', 'RESERVED_NO',
                                'RESERVED_YES', 'TERRAINOCCLUSION_NO', 'TERRAINOCCLUSION_YES', 'DROPPEDFRAME_NO',
                                'DROPPEDFRAME_YES', 'DESIGNATEDFILL_NO', 'DESIGNATEDFILL_YES'
        @type in_criteria_list List
        @param in_rows The number of rows in both input bands.
        @type: in_rows int
        @param in_cols The number of columns in both input bands.
        @type: in_cols int
        @param in_geotransform The geographic transformation to be applied to the output image.
        @type in_geotransform Tuple (as returned by GetGeoTransform())
        @param out_tiff Path to the desired output mask .tif file.
        @type: out_tiff String (should end in ".tif")
        @return None
    """

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
