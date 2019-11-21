import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


def reclass_coloring(src_path, dst_path, reform_dic):
    with rasterio.open(src_path) as src:
        src_arr = src.read(1)
        meta = src.meta
    threshold = reform_dic['threshold']
    dst_value = reform_dic['dst_value']
    color_map = reform_dic['color_map']
    # reclass
    if len(threshold) != len(dst_value):
        print('the input out_value do not match threshold!')
        return
    dst_arr = src_arr.copy()
    for i in range(len(threshold)):
        if i != (len(threshold) - 1):
            dst_arr[(src_arr >= threshold[i]) & (src_arr < threshold[i + 1])] = dst_value[i]
        else:
            dst_arr[src_arr >= threshold[i]] = dst_value[i]
    # coloring
    dst_arr[np.isnan(dst_arr)] = 0
    meta.update({'nodata': 0})
    meta.update({'dtype': 'uint8'})
    with rasterio.open(dst_path, 'w', **meta) as dst:
        dst_arr = dst_arr.astype('uint8')
        dst.write(dst_arr, indexes=1)
        dst.write_colormap(1, color_map)


def reproject2wgs84(src_path, dst_path):
    dataset = rasterio.open(src_path)
    dataread = dataset.read()
    dataread = dataread.astype('uint8')
    dst_crs = 'EPSG:4326'
    transform, width, height = calculate_default_transform(
        dataset.crs, dst_crs, dataset.width, dataset.height, *dataset.bounds)
    kwargs = dataset.profile.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height,
        'dtype': rasterio.uint8,
    })
    with rasterio.open(dst_path, 'w', **kwargs) as dst:
        for i in range(1, dataset.count + 1):
            reproject(
                source=dataread[i - 1],
                destination=rasterio.band(dst, i),
                src_transform=dataset.transform,
                src_crs=dataset.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest)

if __name__ == '__main__':
    src_file = r'F:\zsk\哨兵\千岛湖\悬浮物浓度\悬浮物浓度_千岛湖_20190926.tif'
    reclass_file = src_file.split('.')[0] + '_color.tif'
    dst_file = reclass_file.split('.')[0] + '_reprojected.tif'
    reform_dic = {'threshold': [-1400, 1000, 2000, 3000, 4000],
                  'dst_value': [1, 2, 3, 4, 5],
                  'color_map': {
                      1: (32, 153, 143),
                      2: (0, 219, 0),
                      3: (255, 255, 0),
                      4: (237, 161, 19),
                      5: (194, 82, 60)}}
    reclass_coloring(src_file, reclass_file, reform_dic)
    reproject2wgs84(reclass_file, dst_file)