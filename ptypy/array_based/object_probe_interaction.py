'''
object_probe_interaction

Contains things pertinent to the probe and object interaction.
Should have all the engine updates
'''

import numpy as np
from array_utils import norm2, complex_gaussian_filter, abs2, mass_center, interpolated_shift, clip_complex_magnitudes_to_range
from . import COMPLEX_TYPE


def difference_map_realspace_constraint(probe_and_object, exit_wave, alpha):
    '''
    in theory this can just be called in ptypy instead of get_exit_wave
    '''
    return (1.0 + alpha) * probe_and_object - alpha*exit_wave


def scan_and_multiply(probe, obj, exit_shape, addresses):
    sh = exit_shape
    po = np.zeros((sh[0], sh[1], sh[2]), dtype=COMPLEX_TYPE)
    for pa, oa, ea, _da, _ma in addresses:
        po[ea[0]] = np.multiply(probe[pa[0], pa[1]:(pa[1] + sh[1]), pa[2]:(pa[2] + sh[2])],
                             obj[oa[0], oa[1]:(oa[1] + sh[1]), oa[2]:(oa[2] + sh[2])])
    return po


def difference_map_update_object(ob, object_weights, probe, exit_wave, addr_info, cfact_object, ob_smooth_std=None, clip_object=None):
    pa, oa, ea, _da, _ma = zip(*addr_info)

    if ob_smooth_std is not None:
        smooth_mfs = [0, ob_smooth_std, ob_smooth_std]
        ob[:] = cfact_object * complex_gaussian_filter(ob, smooth_mfs)
    else:
        ob[:] *= cfact_object

    extract_array_from_exit_wave(exit_wave, ea, probe, pa, ob, oa, cfact_object, object_weights)

    if clip_object is not None:
        clip_min, clip_max = clip_object
        clip_complex_magnitudes_to_range(ob, clip_min, clip_max)


def difference_map_update_probe(ob, probe_weights, probe, exit_wave, addr_info, cfact_probe, probe_support=None):
    pa, oa, ea, _da, _ma = zip(*addr_info)
    old_probe = probe
    probe *= cfact_probe
    extract_array_from_exit_wave(exit_wave, ea, ob, oa, probe, pa, cfact_probe, probe_weights)
    if probe_support is not None:
        probe *= probe_support

    change = norm2(probe - old_probe) /norm2(probe)

    return np.sqrt(change / probe.shape[0])


def extract_array_from_exit_wave(exit_wave, exit_addr, array_to_be_extracted, extract_addr, array_to_be_updated, update_addr, cfact, weights):
    sh = exit_wave.shape
    for pa, oa, ea in zip(update_addr, extract_addr, exit_addr):
        extracted_array = array_to_be_extracted[oa[0], oa[1]:(oa[1] + sh[1]), oa[2]:(oa[2] + sh[2])]
        extracted_array_conj = extracted_array.conj()
        array_to_be_updated[pa[0], pa[1]:(pa[1] + sh[1]), pa[2]:(pa[2] + sh[2])] += extracted_array_conj * \
                                                                                    exit_wave[ea[0]] * \
                                                                                    weights[pa[0]]
        cfact[pa[0], pa[1]:(pa[1] + sh[1]), pa[2]:(pa[2] + sh[2])] += extracted_array * \
                                                                      extracted_array_conj * \
                                                                      weights[pa[0]]
    array_to_be_updated /= cfact


def center_probe(probe, center_tolerance):
    c1 = np.array(mass_center(abs2(probe).sum(axis=0)))
    c2 = np.array(probe.shape[-2:]) // 2
    if np.sqrt(norm2(c1 - c2)) < center_tolerance:
        return
    offset = c2-c1
    for idx in range(probe.shape[0]):
        probe[idx] = interpolated_shift(probe[idx], offset)


