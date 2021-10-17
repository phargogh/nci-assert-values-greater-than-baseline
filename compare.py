import sys
import os
import os.path
import logging

import taskgraph
import pygeoprocessing
import numpy
import numpy.testing

logging.basicConfig(level=logging.DEBUG)

BASELINE = 'restoration'
PREFIX = 'noxn_in_drinking_water'
BYTE_NODATA = 255


def main():
    source_directory = sys.argv[1]
    target_workspace = sys.argv[2]
    if not os.path.exists(target_workspace):
        os.makedirs(target_workspace)

    tg_directory = os.path.join(target_workspace, '_taskgraph_db')

    graph = taskgraph.TaskGraph(tg_directory, n_workers=8)

    baseline_scenario_raster = os.path.join(
        source_directory, f'{PREFIX}_{BASELINE}.tif')
    source_raster_info = pygeoprocessing.get_raster_info(
        baseline_scenario_raster)

    target_raster_paths = []
    for scenario_raster in glob.glob(os.path.join(source_directory, '*.tif')):
        if f'{PREFIX}_{BASELINE}.tif' in scenario_raster:
            continue

        # No need to assert raster dimensions ahead of time, just add to graph.
        # raster_calculator will assert dimensions.
        scenario_raster_info = pygeoprocessing.get_raster_info(scenario_raster)
        target_raster_path = os.path.join(
            target_workspace, f'qa_{PREFIX}_{scenario}.tif')
        target_raster_paths.append(target_raster_path)
        graph.add_task(
            pygeoprocessing.raster_calculator,
            args=(
                [(baseline_scenario_raster, 1),
                 (scenario_raster, 1),
                 (source_raster_info['nodata'][0], 'raw'),
                 (scenario_raster_info['nodata'][0], 'raw')],
                _check_values,
                target_raster_path,
                gdal.GDT_Byte,
                BYTE_NODATA),
            target_path_list=[target_raster_path],
            task_name=f'check {scenario}')

    task_graph.close()
    task_graph.join()

    with open(os.path.join(target_workspace, 'summary.txt')) as summary:
        for target_raster_path in target_raster_paths:
            raster = gdal.Open(target_raster_path)
            band = raster.GetRasterBand(1)
            summary.write(str(band.GetStatistics()))


def _check_values(baseline, other, baseline_nodata, other_nodata):
    target_matrix = numpy.full(baseline.shape, BYTE_NODATA, dtype=numpy.uint8)

    valid = numpy.ones(baseline.shape, dtype=bool)
    if baseline_nodata is not None:
        valid &= (~numpy.isclose(baseline, baseline_nodata))

    if other_nodata is not None:
        valid &= (~numpy.isclose(other, other_nodata))

    other_greater_than_baseline = (other[valid] > baseline[valid])

    target_matrix[valid & other_greater_than_baseline] = 1
    target_matrix[valid & ~other_greater_than_baseline] = 0
    return target_matrix


def test():
    baseline = numpy.array([
        [0, 1],
        [2, 3]], dtype=numpy.float32)
    baseline_nodata = 1

    other = numpy.array([
        [1, 2],
        [3, 0]], dtype=numpy.float32)
    other_nodata = 3

    result = _check_values(baseline, other, baseline_nodata, other_nodata)

    expected_result = numpy.array([
        [1, BYTE_NODATA],
        [BYTE_NODATA, 0]], dtype=numpy.uint8)
    numpy.testing.assert_equal(result, expected_result)


def test_greater_than():
    pass

def test_less_than():
    # make a sample baseline raster
    # make a sample 'other' raster
    # run
    # assert results
    pass


if __name__ == '__main__':
    test()
    #main()
