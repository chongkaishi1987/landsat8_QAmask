import datetime
import gdal
from gdal import Open
from landsat8_QAmask import qa_mask

gdal.UseExceptions()
qa_tiff = Open(r'LANDSAT8_QA.TIF')
qa_band = qa_tiff.GetRasterBand(1)

rows, cols, geotransform = qa_tiff.RasterYSize, qa_tiff.RasterXSize, qa_tiff.GetGeoTransform()

print('starting at {0}'.format(datetime.datetime.now().time().isoformat()))
qa_mask(qa_band, ['CLOUD_YES', 'VEGETATION_NO', 'WATER_YES'], rows, cols, geotransform, r'OUTPUT.TIF')
print('done at {0}'.format(datetime.datetime.now().time().isoformat()))