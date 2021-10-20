import sys
import os
import os.path
import logging
import glob

import taskgraph
import pygeoprocessing
import numpy
import numpy.testing
from osgeo import gdal

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)
BASELINE = 'restoration'
PREFIX = 'noxn_in_drinking_water'
BYTE_NODATA = 255


def main():
    source_directory = sys.argv[1]
    target_workspace = sys.argv[2]
    if not os.path.exists(target_workspace):
        os.makedirs(target_workspace)

    tg_directory = os.path.join(target_workspace, '_taskgraph_db')

    graph = taskgraph.TaskGraph(tg_directory, n_workers=16)
    #graph = taskgraph.TaskGraph(tg_directory, n_workers=-1)

    restoration_scenario_raster = os.path.join(
        source_directory, f'{PREFIX}_{BASELINE}.tif')
    source_raster_info = pygeoprocessing.get_raster_info(
        restoration_scenario_raster)

    target_raster_paths = []
    for scenario_raster in glob.glob(os.path.join(source_directory, '*.tif')):
        LOGGER.info(f'Making a task for {scenario_raster}')
        if f'{PREFIX}_{BASELINE}.tif' in scenario_raster:
            continue

        scenario = os.path.splitext(os.path.basename(scenario_raster))[0]

        # No need to assert raster dimensions ahead of time, just add to graph.
        # raster_calculator will assert dimensions.
        scenario_raster_info = pygeoprocessing.get_raster_info(scenario_raster)
        target_raster_path = os.path.join(
            target_workspace, f'qa_{PREFIX}_{scenario}.tif')
        target_raster_paths.append(target_raster_path)
        graph.add_task(
            pygeoprocessing.raster_calculator,
            args=(
                [(restoration_scenario_raster, 1),
                 (scenario_raster, 1),
                 (source_raster_info['nodata'][0], 'raw'),
                 (scenario_raster_info['nodata'][0], 'raw')],
                _check_values,
                target_raster_path,
                gdal.GDT_Byte,
                BYTE_NODATA),
            target_path_list=[target_raster_path],
            task_name=f'check {scenario}')

    graph.close()
    graph.join()

    summary_file = os.path.join(target_workspace, 'summary.txt')
    with open(summary_file, 'w') as summary:
        for target_raster_path in target_raster_paths:
            raster = gdal.Open(target_raster_path)
            band = raster.GetRasterBand(1)
            min, max, mean, stddev = band.GetStatistics(0, 0)
            summary_string = f'{target_raster_path}, min:{min}, max:{max}, mean:{mean}, stddev:{stddev}\n'
            summary.write(summary_string)

    for line in open(summary_file):
        print(line.strip())


def _check_values(restoration, other, restoration_nodata, other_nodata):
    target_matrix = numpy.full(restoration.shape, BYTE_NODATA, dtype=numpy.uint8)

    valid = numpy.ones(restoration.shape, dtype=bool)
    if restoration_nodata is not None:
        valid &= (~numpy.isclose(restoration, restoration_nodata))

    if other_nodata is not None:
        valid &= (~numpy.isclose(other, other_nodata))

    if numpy.count_nonzero(valid) == 0:
        return target_matrix

    # if restoration >= other, value of 1
    # else value of 0
    # nodata if not valid (either restoration or other are nodata)
    target_matrix[valid] = (restoration[valid] >= other[valid])

    return target_matrix


def test():
    LOGGER.info('Testing')
    restoration = numpy.array([
        [0, 1],
        [2, 3]], dtype=numpy.float32)
    restoration_nodata = 1

    other = numpy.array([
        [1, 2],
        [3, 0]], dtype=numpy.float32)
    other_nodata = 3

    result = _check_values(restoration, other, restoration_nodata, other_nodata)

    expected_result = numpy.array([
        [0, BYTE_NODATA],
        [BYTE_NODATA, 1]], dtype=numpy.uint8)
    numpy.testing.assert_equal(result, expected_result)
    LOGGER.info('Test passed')


if __name__ == '__main__':
    test()
    main()
