from __future__ import print_function, division, absolute_import

import time

import matplotlib
matplotlib.use('Agg')  # fix execution of tests involving matplotlib on travis
import numpy as np
import six.moves as sm

import imgaug as ia
from imgaug import augmenters as iaa
from imgaug import parameters as iap
from imgaug.testutils import array_equal_lists, keypoints_equal, reseed


def main():
    time_start = time.time()

    test_Scale()
    # TODO test_CropAndPad()
    test_Pad()
    test_Crop()
    test_PadToFixedSize()
    test_CropToFixedSize()

    time_end = time.time()
    print("<%s> Finished without errors in %.4fs." % (__file__, time_end - time_start,))


def test_Scale():
    reseed()

    base_img2d = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 255, 255, 255, 255, 255, 255, 0],
        [0, 255, 255, 255, 255, 255, 255, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]
    base_img2d = np.array(base_img2d, dtype=np.uint8)
    base_img3d = np.tile(base_img2d[..., np.newaxis], (1, 1, 3))

    intensity_avg = np.average(base_img2d)
    intensity_low = intensity_avg - 0.2 * np.abs(intensity_avg - 128)
    intensity_high = intensity_avg + 0.2 * np.abs(intensity_avg - 128)

    aspect_ratio2d = base_img2d.shape[1] / base_img2d.shape[0]
    aspect_ratio3d = base_img3d.shape[1] / base_img3d.shape[0]

    aug = iaa.Scale(12)
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (12, 12)
    assert observed3d.shape == (12, 12, 3)
    assert 50 < np.average(observed2d) < 205
    assert 50 < np.average(observed3d) < 205

    aug = iaa.Scale({"height": 8, "width": 12})
    heatmaps_arr = (base_img2d / 255.0).astype(np.float32)
    heatmaps_aug = aug.augment_heatmaps([ia.HeatmapsOnImage(heatmaps_arr, shape=base_img3d.shape)])[0]
    assert heatmaps_aug.shape == (8, 12, 3)
    assert 0 - 1e-6 < heatmaps_aug.min_value < 0 + 1e-6
    assert 1 - 1e-6 < heatmaps_aug.max_value < 1 + 1e-6
    assert np.average(heatmaps_aug.get_arr()[0, :]) < 0.05
    assert np.average(heatmaps_aug.get_arr()[-1, :]) < 0.05
    assert np.average(heatmaps_aug.get_arr()[:, 0]) < 0.05
    assert 0.8 < np.average(heatmaps_aug.get_arr()[2:6, 2:10]) < 1 + 1e-6

    aug = iaa.Scale([12, 14])
    seen2d = [False, False]
    seen3d = [False, False]
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in [(12, 12), (14, 14)]
        assert observed3d.shape in [(12, 12, 3), (14, 14, 3)]
        if observed2d.shape == (12, 12):
            seen2d[0] = True
        else:
            seen2d[1] = True
        if observed3d.shape == (12, 12, 3):
            seen3d[0] = True
        else:
            seen3d[1] = True
        if all(seen2d) and all(seen3d):
            break
    assert all(seen2d)
    assert all(seen3d)

    aug = iaa.Scale((12, 14))
    seen2d = [False, False, False]
    seen3d = [False, False, False]
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in [(12, 12), (13, 13), (14, 14)]
        assert observed3d.shape in [(12, 12, 3), (13, 13, 3), (14, 14, 3)]
        if observed2d.shape == (12, 12):
            seen2d[0] = True
        elif observed2d.shape == (13, 13):
            seen2d[1] = True
        else:
            seen2d[2] = True
        if observed3d.shape == (12, 12, 3):
            seen3d[0] = True
        elif observed3d.shape == (13, 13, 3):
            seen3d[1] = True
        else:
            seen3d[2] = True
        if all(seen2d) and all(seen3d):
            break
    assert all(seen2d)
    assert all(seen3d)

    aug = iaa.Scale("keep")
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == base_img2d.shape
    assert observed3d.shape == base_img3d.shape

    aug = iaa.Scale([])
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == base_img2d.shape
    assert observed3d.shape == base_img3d.shape

    aug = iaa.Scale({})
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == base_img2d.shape
    assert observed3d.shape == base_img3d.shape

    aug = iaa.Scale({"height": 11})
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (11, base_img2d.shape[1])
    assert observed3d.shape == (11, base_img3d.shape[1], 3)

    aug = iaa.Scale({"width": 13})
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (base_img2d.shape[0], 13)
    assert observed3d.shape == (base_img3d.shape[0], 13, 3)

    aug = iaa.Scale({"height": 12, "width": 13})
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (12, 13)
    assert observed3d.shape == (12, 13, 3)

    aug = iaa.Scale({"height": 12, "width": "keep"})
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (12, base_img2d.shape[1])
    assert observed3d.shape == (12, base_img3d.shape[1], 3)

    aug = iaa.Scale({"height": "keep", "width": 12})
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (base_img2d.shape[0], 12)
    assert observed3d.shape == (base_img3d.shape[0], 12, 3)

    aug = iaa.Scale({"height": 12, "width": "keep-aspect-ratio"})
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (12, int(12 * aspect_ratio2d))
    assert observed3d.shape == (12, int(12 * aspect_ratio3d), 3)

    aug = iaa.Scale({"height": "keep-aspect-ratio", "width": 12})
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (int(12 * (1/aspect_ratio2d)), 12)
    assert observed3d.shape == (int(12 * (1/aspect_ratio3d)), 12, 3)

    aug = iaa.Scale({"height": [12, 14], "width": 12})
    seen2d = [False, False]
    seen3d = [False, False]
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in [(12, 12), (14, 12)]
        assert observed3d.shape in [(12, 12, 3), (14, 12, 3)]
        if observed2d.shape == (12, 12):
            seen2d[0] = True
        else:
            seen2d[1] = True
        if observed3d.shape == (12, 12, 3):
            seen3d[0] = True
        else:
            seen3d[1] = True
        if all(seen2d) and all(seen3d):
            break
    assert all(seen2d)
    assert all(seen3d)

    aug = iaa.Scale({"height": 12, "width": [12, 14]})
    seen2d = [False, False]
    seen3d = [False, False]
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in [(12, 12), (12, 14)]
        assert observed3d.shape in [(12, 12, 3), (12, 14, 3)]
        if observed2d.shape == (12, 12):
            seen2d[0] = True
        else:
            seen2d[1] = True
        if observed3d.shape == (12, 12, 3):
            seen3d[0] = True
        else:
            seen3d[1] = True
        if all(seen2d) and all(seen3d):
            break
    assert all(seen2d)
    assert all(seen3d)

    aug = iaa.Scale({"height": 12, "width": iap.Choice([12, 14])})
    seen2d = [False, False]
    seen3d = [False, False]
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in [(12, 12), (12, 14)]
        assert observed3d.shape in [(12, 12, 3), (12, 14, 3)]
        if observed2d.shape == (12, 12):
            seen2d[0] = True
        else:
            seen2d[1] = True
        if observed3d.shape == (12, 12, 3):
            seen3d[0] = True
        else:
            seen3d[1] = True
        if all(seen2d) and all(seen3d):
            break
    assert all(seen2d)
    assert all(seen3d)

    aug = iaa.Scale({"height": (12, 14), "width": 12})
    seen2d = [False, False, False]
    seen3d = [False, False, False]
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in [(12, 12), (13, 12), (14, 12)]
        assert observed3d.shape in [(12, 12, 3), (13, 12, 3), (14, 12, 3)]
        if observed2d.shape == (12, 12):
            seen2d[0] = True
        elif observed2d.shape == (13, 12):
            seen2d[1] = True
        else:
            seen2d[2] = True
        if observed3d.shape == (12, 12, 3):
            seen3d[0] = True
        elif observed3d.shape == (13, 12, 3):
            seen3d[1] = True
        else:
            seen3d[2] = True
        if all(seen2d) and all(seen3d):
            break
    assert all(seen2d)
    assert all(seen3d)

    aug = iaa.Scale(2.0)
    observed2d = aug.augment_image(base_img2d)
    observed3d = aug.augment_image(base_img3d)
    assert observed2d.shape == (base_img2d.shape[0]*2, base_img2d.shape[1]*2)
    assert observed3d.shape == (base_img3d.shape[0]*2, base_img3d.shape[1]*2, 3)
    assert intensity_low < np.average(observed2d) < intensity_high
    assert intensity_low < np.average(observed3d) < intensity_high

    aug = iaa.Scale([2.0, 4.0])
    seen2d = [False, False]
    seen3d = [False, False]
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in [(base_img2d.shape[0]*2, base_img2d.shape[1]*2),
                                    (base_img2d.shape[0]*4, base_img2d.shape[1]*4)]
        assert observed3d.shape in [(base_img3d.shape[0]*2, base_img3d.shape[1]*2, 3),
                                    (base_img3d.shape[0]*4, base_img3d.shape[1]*4, 3)]
        if observed2d.shape == (base_img2d.shape[0]*2, base_img2d.shape[1]*2):
            seen2d[0] = True
        else:
            seen2d[1] = True
        if observed3d.shape == (base_img3d.shape[0]*2, base_img3d.shape[1]*2, 3):
            seen3d[0] = True
        else:
            seen3d[1] = True
        if all(seen2d) and all(seen3d):
            break
    assert all(seen2d)
    assert all(seen3d)

    aug = iaa.Scale(iap.Choice([2.0, 4.0]))
    seen2d = [False, False]
    seen3d = [False, False]
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in [(base_img2d.shape[0]*2, base_img2d.shape[1]*2),
                                    (base_img2d.shape[0]*4, base_img2d.shape[1]*4)]
        assert observed3d.shape in [(base_img3d.shape[0]*2, base_img3d.shape[1]*2, 3),
                                    (base_img3d.shape[0]*4, base_img3d.shape[1]*4, 3)]
        if observed2d.shape == (base_img2d.shape[0]*2, base_img2d.shape[1]*2):
            seen2d[0] = True
        else:
            seen2d[1] = True
        if observed3d.shape == (base_img3d.shape[0]*2, base_img3d.shape[1]*2, 3):
            seen3d[0] = True
        else:
            seen3d[1] = True
        if all(seen2d) and all(seen3d):
            break
    assert all(seen2d)
    assert all(seen3d)

    base_img2d = base_img2d[0:4, 0:4]
    base_img3d = base_img3d[0:4, 0:4, :]
    aug = iaa.Scale((0.76, 1.0))
    not_seen2d = set()
    not_seen3d = set()
    for size in sm.xrange(3, 4+1):
        not_seen2d.add((size, size))
    for size in sm.xrange(3, 4+1):
        not_seen3d.add((size, size, 3))
    possible2d = set(list(not_seen2d))
    possible3d = set(list(not_seen3d))
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in possible2d
        assert observed3d.shape in possible3d
        if observed2d.shape in not_seen2d:
            not_seen2d.remove(observed2d.shape)
        if observed3d.shape in not_seen3d:
            not_seen3d.remove(observed3d.shape)
        if not not_seen2d and not not_seen3d:
            break
    assert not not_seen2d
    assert not not_seen3d

    base_img2d = base_img2d[0:4, 0:4]
    base_img3d = base_img3d[0:4, 0:4, :]
    aug = iaa.Scale({"height": (0.76, 1.0), "width": (0.76, 1.0)})
    not_seen2d = set()
    not_seen3d = set()
    for hsize in sm.xrange(3, 4+1):
        for wsize in sm.xrange(3, 4+1):
            not_seen2d.add((hsize, wsize))
    for hsize in sm.xrange(3, 4+1):
        for wsize in sm.xrange(3, 4+1):
            not_seen3d.add((hsize, wsize, 3))
    possible2d = set(list(not_seen2d))
    possible3d = set(list(not_seen3d))
    for _ in sm.xrange(100):
        observed2d = aug.augment_image(base_img2d)
        observed3d = aug.augment_image(base_img3d)
        assert observed2d.shape in possible2d
        assert observed3d.shape in possible3d
        if observed2d.shape in not_seen2d:
            not_seen2d.remove(observed2d.shape)
        if observed3d.shape in not_seen3d:
            not_seen3d.remove(observed3d.shape)
        if not not_seen2d and not not_seen3d:
            break
    assert not not_seen2d
    assert not not_seen3d

    got_exception = False
    try:
        aug = iaa.Scale("foo")
        observed2d = aug.augment_image(base_img2d)
    except Exception as exc:
        assert "Expected " in str(exc)
        got_exception = True
    assert got_exception

    aug = iaa.Scale(size=1, interpolation="nearest")
    params = aug.get_parameters()
    assert isinstance(params[0], iap.Deterministic)
    assert isinstance(params[1], iap.Deterministic)
    assert params[0].value == 1
    assert params[1].value == "nearest"


def test_Pad():
    reseed()

    base_img = np.array([[0, 0, 0],
                         [0, 1, 0],
                         [0, 0, 0]], dtype=np.uint8)
    base_img = base_img[:, :, np.newaxis]

    images = np.array([base_img])
    images_list = [base_img]

    keypoints = [ia.KeypointsOnImage([ia.Keypoint(x=0, y=0), ia.Keypoint(x=1, y=1),
                                      ia.Keypoint(x=2, y=2)], shape=base_img.shape)]

    heatmaps_arr = np.float32([[0, 0, 0],
                               [0, 1.0, 0],
                               [0, 0, 0]])

    # test pad by 1 pixel on each side
    pads = [
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    ]
    for pad in pads:
        top, right, bottom, left = pad
        aug = iaa.Pad(px=pad, keep_size=False)
        base_img_padded = np.pad(base_img, ((top, bottom), (left, right), (0, 0)),
                                 mode="constant",
                                 constant_values=0)
        observed = aug.augment_images(images)
        assert np.array_equal(observed, np.array([base_img_padded]))

        observed = aug.augment_images(images_list)
        assert array_equal_lists(observed, [base_img_padded])

        keypoints_moved = [keypoints[0].shift(x=left, y=top)]
        observed = aug.augment_keypoints(keypoints)
        assert keypoints_equal(observed, keypoints_moved)

        # heatmaps
        aug = iaa.Pad(px=pad, keep_size=False)
        heatmaps_arr_padded = np.pad(heatmaps_arr, ((top, bottom), (left, right)),
                                     mode="constant",
                                     constant_values=0)
        observed = aug.augment_heatmaps([ia.HeatmapsOnImage(heatmaps_arr, shape=base_img.shape)])[0]
        assert observed.shape == base_img_padded.shape
        assert 0 - 1e-6 < observed.min_value < 0 + 1e-6
        assert 1 - 1e-6 < observed.max_value < 1 + 1e-6
        assert np.array_equal(observed.get_arr(), heatmaps_arr_padded)

    # test pad by range of pixels
    pads = [
        ((0, 2), 0, 0, 0),
        (0, (0, 2), 0, 0),
        (0, 0, (0, 2), 0),
        (0, 0, 0, (0, 2)),
    ]
    for pad in pads:
        top, right, bottom, left = pad
        aug = iaa.Pad(px=pad, keep_size=False)
        aug_det = aug.to_deterministic()

        images_padded = []
        keypoints_padded = []
        top_range = top if isinstance(top, tuple) else (top, top)
        right_range = right if isinstance(right, tuple) else (right, right)
        bottom_range = bottom if isinstance(bottom, tuple) else (bottom, bottom)
        left_range = left if isinstance(left, tuple) else (left, left)
        for top_val in sm.xrange(top_range[0], top_range[1]+1):
            for right_val in sm.xrange(right_range[0], right_range[1]+1):
                for bottom_val in sm.xrange(bottom_range[0], bottom_range[1]+1):
                    for left_val in sm.xrange(left_range[0], left_range[1]+1):
                        images_padded.append(
                            np.pad(base_img, ((top_val, bottom_val), (left_val, right_val), (0, 0)),
                                   mode="constant", constant_values=0)
                        )
                        keypoints_padded.append(keypoints[0].shift(x=left_val, y=top_val))

        movements = []
        movements_det = []
        for i in sm.xrange(100):
            observed = aug.augment_images(images)

            matches = [1 if np.array_equal(observed, np.array([base_img_padded])) else 0
                       for base_img_padded in images_padded]
            movements.append(np.argmax(np.array(matches)))
            assert any([val == 1 for val in matches])

            observed = aug_det.augment_images(images)
            matches = [1 if np.array_equal(observed, np.array([base_img_padded])) else 0
                       for base_img_padded in images_padded]
            movements_det.append(np.argmax(np.array(matches)))
            assert any([val == 1 for val in matches])

            observed = aug.augment_images(images_list)
            assert any([array_equal_lists(observed, [base_img_padded])
                        for base_img_padded in images_padded])

            observed = aug.augment_keypoints(keypoints)
            assert any([keypoints_equal(observed, [kp]) for kp in keypoints_padded])

        assert len(set(movements)) == 3
        assert len(set(movements_det)) == 1

    # test pad by list of exact pixel values
    pads = [
        ([0, 2], 0, 0, 0),
        (0, [0, 2], 0, 0),
        (0, 0, [0, 2], 0),
        (0, 0, 0, [0, 2]),
    ]
    for pad in pads:
        top, right, bottom, left = pad
        aug = iaa.Pad(px=pad, keep_size=False)
        aug_det = aug.to_deterministic()

        images_padded = []
        keypoints_padded = []
        top_range = top if isinstance(top, list) else [top]
        right_range = right if isinstance(right, list) else [right]
        bottom_range = bottom if isinstance(bottom, list) else [bottom]
        left_range = left if isinstance(left, list) else [left]
        for top_val in top_range:
            for right_val in right_range:
                for bottom_val in bottom_range:
                    for left_val in left_range:
                        images_padded.append(
                            np.pad(base_img, ((top_val, bottom_val), (left_val, right_val), (0, 0)), mode="constant",
                                   constant_values=0)
                        )
                        keypoints_padded.append(keypoints[0].shift(x=left_val, y=top_val))

        movements = []
        movements_det = []
        for i in sm.xrange(100):
            observed = aug.augment_images(images)
            matches = [1 if np.array_equal(observed, np.array([base_img_padded])) else 0
                       for base_img_padded in images_padded]
            movements.append(np.argmax(np.array(matches)))
            assert any([val == 1 for val in matches])

            observed = aug_det.augment_images(images)
            matches = [1 if np.array_equal(observed, np.array([base_img_padded])) else 0
                       for base_img_padded in images_padded]
            movements_det.append(np.argmax(np.array(matches)))
            assert any([val == 1 for val in matches])

            observed = aug.augment_images(images_list)
            assert any([array_equal_lists(observed, [base_img_padded])
                        for base_img_padded in images_padded])

            observed = aug.augment_keypoints(keypoints)
            assert any([keypoints_equal(observed, [kp]) for kp in keypoints_padded])

        assert len(set(movements)) == 2
        assert len(set(movements_det)) == 1

    # pad modes
    image = np.zeros((1, 2), dtype=np.uint8)
    image[0, 0] = 100
    image[0, 1] = 50
    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode=iap.Choice(["constant", "maximum", "edge"]), pad_cval=0, keep_size=False)
    seen = [0, 0, 0]
    for _ in sm.xrange(300):
        observed = aug.augment_image(image)
        if observed[0, 2] == 0:
            seen[0] += 1
        elif observed[0, 2] == 100:
            seen[1] += 1
        elif observed[0, 2] == 50:
            seen[2] += 1
        else:
            assert False
    assert all([100 - 50 < v < 100 + 50 for v in seen])

    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode=ia.ALL, pad_cval=0, keep_size=False)
    expected = ["constant", "edge", "linear_ramp", "maximum", "median", "minimum", "reflect", "symmetric", "wrap"]
    assert isinstance(aug.pad_mode, iap.Choice)
    assert len(aug.pad_mode.a) == len(expected)
    assert all([v in aug.pad_mode.a for v in expected])

    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode=["constant", "maximum"], pad_cval=0, keep_size=False)
    expected = ["constant", "maximum"]
    assert isinstance(aug.pad_mode, iap.Choice)
    assert len(aug.pad_mode.a) == len(expected)
    assert all([v in aug.pad_mode.a for v in expected])

    got_exception = False
    try:
        _aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode=False, pad_cval=0, keep_size=False)
    except Exception as exc:
        assert "Expected pad_mode to be " in str(exc)
        got_exception = True
    assert got_exception

    # pad modes, heatmaps
    heatmaps = ia.HeatmapsOnImage(np.ones((3, 3, 1), dtype=np.float32), shape=(3, 3, 3))
    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode="edge", pad_cval=0, keep_size=False)
    observed = aug.augment_heatmaps([heatmaps])[0]
    assert np.sum(observed.get_arr() <= 1e-4) == 3

    # pad cvals
    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode="constant", pad_cval=100, keep_size=False)
    observed = aug.augment_image(np.zeros((1, 1), dtype=np.uint8))
    assert observed[0, 0] == 0
    assert observed[0, 1] == 100

    image = np.zeros((1, 1), dtype=np.uint8)
    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode="constant", pad_cval=iap.Choice([50, 100]), keep_size=False)
    seen = [0, 0]
    for _ in sm.xrange(200):
        observed = aug.augment_image(image)
        if observed[0, 1] == 50:
            seen[0] += 1
        elif observed[0, 1] == 100:
            seen[1] += 1
        else:
            assert False
    assert all([100 - 50 < v < 100 + 50 for v in seen])

    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode="constant", pad_cval=[50, 100], keep_size=False)
    expected = [50, 100]
    assert isinstance(aug.pad_cval, iap.Choice)
    assert len(aug.pad_cval.a) == len(expected)
    assert all([v in aug.pad_cval.a for v in expected])

    image = np.zeros((1, 1), dtype=np.uint8)
    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode="constant", pad_cval=(50, 52), keep_size=False)
    seen = [0, 0, 0]
    for _ in sm.xrange(300):
        observed = aug.augment_image(image)
        if observed[0, 1] == 50:
            seen[0] += 1
        elif observed[0, 1] == 51:
            seen[1] += 1
        elif observed[0, 1] == 52:
            seen[2] += 1
        else:
            assert False
    assert all([100 - 50 < v < 100 + 50 for v in seen])

    got_exception = False
    try:
        aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode="constant", pad_cval="test", keep_size=False)
    except Exception as exc:
        assert "Expected " in str(exc)
        got_exception = True
    assert got_exception

    # pad cvals, heatmaps
    heatmaps = ia.HeatmapsOnImage(np.zeros((3, 3, 1), dtype=np.float32), shape=(3, 3, 3))
    aug = iaa.Pad(px=(0, 1, 0, 0), pad_mode="constant", pad_cval=255, keep_size=False)
    observed = aug.augment_heatmaps([heatmaps])[0]
    assert np.sum(observed.get_arr() > 1e-4) == 0

    # ------------------
    # pad by percentages
    # ------------------
    # pad all sides by 100%
    aug = iaa.Pad(percent=1.0, keep_size=False)
    observed = aug.augment_image(np.zeros((4, 4), dtype=np.uint8) + 1)
    assert observed.shape == (4+4+4, 4+4+4)
    assert np.sum(observed[4:-4, 4:-4]) == 4*4
    assert np.sum(observed) == 4*4

    # pad all sides by StochasticParameter
    aug = iaa.Pad(percent=iap.Deterministic(1.0), keep_size=False)
    observed = aug.augment_image(np.zeros((4, 4), dtype=np.uint8) + 1)
    assert observed.shape == (4+4+4, 4+4+4)
    assert np.sum(observed[4:-4, 4:-4]) == 4*4
    assert np.sum(observed) == 4*4

    # pad all sides by 100-200%
    aug = iaa.Pad(percent=(1.0, 2.0), sample_independently=False, keep_size=False)
    observed = aug.augment_image(np.zeros((4, 4), dtype=np.uint8) + 1)
    assert np.sum(observed) == 4*4
    assert (observed.shape[0] - 4) % 2 == 0
    assert (observed.shape[1] - 4) % 2 == 0

    # pad by invalid value
    got_exception = False
    try:
        _ = iaa.Pad(percent="test", keep_size=False)
    except Exception as exc:
        assert "Expected " in str(exc)
        got_exception = True
    assert got_exception

    # test pad by 100% on each side
    image = np.zeros((4, 4), dtype=np.uint8)
    image[0, 0] = 255
    image[3, 0] = 255
    image[0, 3] = 255
    image[3, 3] = 255
    height, width = image.shape[0:2]
    keypoints = [ia.KeypointsOnImage([ia.Keypoint(x=0, y=0), ia.Keypoint(x=3, y=3),
                                      ia.Keypoint(x=3, y=3)], shape=image.shape)]
    pads = [
        (1.0, 0, 0, 0),
        (0, 1.0, 0, 0),
        (0, 0, 1.0, 0),
        (0, 0, 0, 1.0),
    ]
    for pad in pads:
        top, right, bottom, left = pad
        top_px = int(top * height)
        right_px = int(right * width)
        bottom_px = int(bottom * height)
        left_px = int(left * width)
        aug = iaa.Pad(percent=pad, keep_size=False)
        image_padded = np.pad(image, ((top_px, bottom_px), (left_px, right_px)),
                              mode="constant",
                              constant_values=0)
        observed = aug.augment_image(image)
        assert np.array_equal(observed, image_padded)

        keypoints_moved = [keypoints[0].shift(x=left_px, y=top_px)]
        observed = aug.augment_keypoints(keypoints)
        assert keypoints_equal(observed, keypoints_moved)

    # test pad by range of percentages
    aug = iaa.Pad(percent=((0, 1.0), 0, 0, 0), keep_size=False)
    seen = [0, 0, 0, 0, 0]
    for _ in sm.xrange(500):
        observed = aug.augment_image(np.zeros((4, 4), dtype=np.uint8) + 255)
        n_padded = 0
        while np.all(observed[0, :] == 0):
            n_padded += 1
            observed = observed[1:, :]
        seen[n_padded] += 1
    # note that we cant just check for 100-50 < x < 100+50 here. The first and last value (0px
    # and 4px) padding have half the probability of occuring compared to the other values.
    # E.g. 0px is padded if sampled p falls in range [0, 0.125). 1px is padded if sampled p
    # falls in range [0.125, 0.375].
    assert all([v > 30 for v in seen])

    aug = iaa.Pad(percent=(0, (0, 1.0), 0, 0), keep_size=False)
    seen = [0, 0, 0, 0, 0]
    for _ in sm.xrange(500):
        observed = aug.augment_image(np.zeros((4, 4), dtype=np.uint8) + 255)
        n_padded = 0
        while np.all(observed[:, -1] == 0):
            n_padded += 1
            observed = observed[:, 0:-1]
        seen[n_padded] += 1
    assert all([v > 30 for v in seen])

    # test pad by list of percentages
    aug = iaa.Pad(percent=([0.0, 1.0], 0, 0, 0), keep_size=False)
    seen = [0, 0, 0, 0, 0]
    for _ in sm.xrange(500):
        observed = aug.augment_image(np.zeros((4, 4), dtype=np.uint8) + 255)
        n_padded = 0
        while np.all(observed[0, :] == 0):
            n_padded += 1
            observed = observed[1:, :]
        seen[n_padded] += 1
    assert 250 - 50 < seen[0] < 250 + 50
    assert seen[1] == 0
    assert seen[2] == 0
    assert seen[3] == 0
    assert 250 - 50 < seen[4] < 250 + 50

    aug = iaa.Pad(percent=(0, [0.0, 1.0], 0, 0), keep_size=False)
    seen = [0, 0, 0, 0, 0]
    for _ in sm.xrange(500):
        observed = aug.augment_image(np.zeros((4, 4), dtype=np.uint8) + 255)
        n_padded = 0
        while np.all(observed[:, -1] == 0):
            n_padded += 1
            observed = observed[:, 0:-1]
        seen[n_padded] += 1
    assert 250 - 50 < seen[0] < 250 + 50
    assert seen[1] == 0
    assert seen[2] == 0
    assert seen[3] == 0
    assert 250 - 50 < seen[4] < 250 + 50


def test_Crop():
    reseed()

    base_img = np.array([[0, 0, 0],
                         [0, 1, 0],
                         [0, 0, 0]], dtype=np.uint8)
    base_img = base_img[:, :, np.newaxis]

    images = np.array([base_img])
    images_list = [base_img]

    keypoints = [ia.KeypointsOnImage([ia.Keypoint(x=0, y=0), ia.Keypoint(x=1, y=1),
                                      ia.Keypoint(x=2, y=2)], shape=base_img.shape)]

    heatmaps_arr = np.float32([[0, 0, 0],
                               [0, 1.0, 0],
                               [0, 0, 0]])

    # test crop by 1 pixel on each side
    crops = [
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    ]
    for crop in crops:
        top, right, bottom, left = crop
        height, width = base_img.shape[0:2]
        aug = iaa.Crop(px=crop, keep_size=False)
        base_img_cropped = base_img[top:height-bottom, left:width-right, :]
        observed = aug.augment_images(images)
        assert np.array_equal(observed, np.array([base_img_cropped]))

        observed = aug.augment_images(images_list)
        assert array_equal_lists(observed, [base_img_cropped])

        keypoints_moved = [keypoints[0].shift(x=-left, y=-top)]
        observed = aug.augment_keypoints(keypoints)
        assert keypoints_equal(observed, keypoints_moved)

        height, width = heatmaps_arr.shape[0:2]
        aug = iaa.Crop(px=crop, keep_size=False)
        heatmaps_arr_cropped = heatmaps_arr[top:height-bottom, left:width-right]
        observed = aug.augment_heatmaps([ia.HeatmapsOnImage(heatmaps_arr, shape=base_img.shape)])[0]
        assert observed.shape == base_img_cropped.shape
        assert np.array_equal(observed.get_arr(), heatmaps_arr_cropped)

    # test crop by range of pixels
    crops = [
        ((0, 2), 0, 0, 0),
        (0, (0, 2), 0, 0),
        (0, 0, (0, 2), 0),
        (0, 0, 0, (0, 2)),
    ]
    for crop in crops:
        top, right, bottom, left = crop
        height, width = base_img.shape[0:2]
        aug = iaa.Crop(px=crop, keep_size=False)
        aug_det = aug.to_deterministic()

        images_cropped = []
        keypoints_cropped = []
        top_range = top if isinstance(top, tuple) else (top, top)
        right_range = right if isinstance(right, tuple) else (right, right)
        bottom_range = bottom if isinstance(bottom, tuple) else (bottom, bottom)
        left_range = left if isinstance(left, tuple) else (left, left)
        for top_val in sm.xrange(top_range[0], top_range[1]+1):
            for right_val in sm.xrange(right_range[0], right_range[1]+1):
                for bottom_val in sm.xrange(bottom_range[0], bottom_range[1]+1):
                    for left_val in sm.xrange(left_range[0], left_range[1]+1):

                        images_cropped.append(base_img[top_val:height-bottom_val, left_val:width-right_val, :])
                        keypoints_cropped.append(keypoints[0].shift(x=-left_val, y=-top_val))

        movements = []
        movements_det = []
        for i in sm.xrange(100):
            observed = aug.augment_images(images)

            matches = [1 if np.array_equal(observed, np.array([base_img_cropped])) else 0
                       for base_img_cropped in images_cropped]
            movements.append(np.argmax(np.array(matches)))
            assert any([val == 1 for val in matches])

            observed = aug_det.augment_images(images)
            matches = [1 if np.array_equal(observed, np.array([base_img_cropped])) else 0
                       for base_img_cropped in images_cropped]
            movements_det.append(np.argmax(np.array(matches)))
            assert any([val == 1 for val in matches])

            observed = aug.augment_images(images_list)
            assert any([array_equal_lists(observed, [base_img_cropped])
                        for base_img_cropped in images_cropped])

            observed = aug.augment_keypoints(keypoints)
            assert any([keypoints_equal(observed, [kp]) for kp in keypoints_cropped])

        assert len(set(movements)) == 3
        assert len(set(movements_det)) == 1

    # test crop by list of exact pixel values
    crops = [
        ([0, 2], 0, 0, 0),
        (0, [0, 2], 0, 0),
        (0, 0, [0, 2], 0),
        (0, 0, 0, [0, 2]),
    ]
    for crop in crops:
        top, right, bottom, left = crop
        height, width = base_img.shape[0:2]
        aug = iaa.Crop(px=crop, keep_size=False)
        aug_det = aug.to_deterministic()

        images_cropped = []
        keypoints_cropped = []
        top_range = top if isinstance(top, list) else [top]
        right_range = right if isinstance(right, list) else [right]
        bottom_range = bottom if isinstance(bottom, list) else [bottom]
        left_range = left if isinstance(left, list) else [left]
        for top_val in top_range:
            for right_val in right_range:
                for bottom_val in bottom_range:
                    for left_val in left_range:
                        images_cropped.append(base_img[top_val:height-bottom_val, left_val:width-right_val, :])
                        keypoints_cropped.append(keypoints[0].shift(x=-left_val, y=-top_val))

        movements = []
        movements_det = []
        for i in sm.xrange(100):
            observed = aug.augment_images(images)
            matches = [1 if np.array_equal(observed, np.array([base_img_cropped])) else 0
                       for base_img_cropped in images_cropped]
            movements.append(np.argmax(np.array(matches)))
            assert any([val == 1 for val in matches])

            observed = aug_det.augment_images(images)
            matches = [1 if np.array_equal(observed, np.array([base_img_cropped])) else 0
                       for base_img_cropped in images_cropped]
            movements_det.append(np.argmax(np.array(matches)))
            assert any([val == 1 for val in matches])

            observed = aug.augment_images(images_list)
            assert any([array_equal_lists(observed, [base_img_cropped])
                        for base_img_cropped in images_cropped])

            observed = aug.augment_keypoints(keypoints)
            assert any([keypoints_equal(observed, [kp]) for kp in keypoints_cropped])

        assert len(set(movements)) == 2
        assert len(set(movements_det)) == 1

    # ------------------
    # crop by percentages
    # ------------------
    # crop all sides by 10%
    aug = iaa.Crop(percent=0.1, keep_size=False)
    image = np.random.randint(0, 255, size=(50, 50), dtype=np.uint8)
    observed = aug.augment_image(image)
    assert observed.shape == (40, 40)
    assert np.all(observed == image[5:-5, 5:-5])

    # crop all sides by StochasticParameter
    aug = iaa.Crop(percent=iap.Deterministic(0.1), keep_size=False)
    image = np.random.randint(0, 255, size=(50, 50), dtype=np.uint8)
    observed = aug.augment_image(image)
    assert observed.shape == (40, 40)
    assert np.all(observed == image[5:-5, 5:-5])

    # crop all sides by 10-20%
    image = np.random.randint(0, 255, size=(50, 50), dtype=np.uint8)
    aug = iaa.Crop(percent=(0.1, 0.2), keep_size=False)
    observed = aug.augment_image(image)
    assert 30 <= observed.shape[0] <= 40
    assert 30 <= observed.shape[1] <= 40

    # crop by invalid value
    got_exception = False
    try:
        _ = iaa.Crop(percent="test", keep_size=False)
    except Exception as exc:
        assert "Expected " in str(exc)
        got_exception = True
    assert got_exception

    # test crop by 10% on each side
    image = np.random.randint(0, 255, size=(50, 50), dtype=np.uint8)
    height, width = image.shape[0:2]
    keypoints = [ia.KeypointsOnImage([ia.Keypoint(x=10, y=11), ia.Keypoint(x=20, y=21),
                                      ia.Keypoint(x=30, y=31)], shape=image.shape)]
    crops = [
        (0.1, 0, 0, 0),
        (0, 0.1, 0, 0),
        (0, 0, 0.1, 0),
        (0, 0, 0, 0.1),
    ]
    for crop in crops:
        top, right, bottom, left = crop
        top_px = int(round(top * height))
        right_px = int(round(right * width))
        bottom_px = int(round(bottom * height))
        left_px = int(round(left * width))
        aug = iaa.Crop(percent=crop, keep_size=False)
        # dont use :-bottom_px and ;-right_px here, because these values can be 0
        image_cropped = image[top_px:50-bottom_px, left_px:50-right_px]
        observed = aug.augment_image(image)
        assert np.array_equal(observed, image_cropped)

        keypoints_moved = [keypoints[0].shift(x=-left_px, y=-top_px)]
        observed = aug.augment_keypoints(keypoints)
        assert keypoints_equal(observed, keypoints_moved)

    # test crop by range of percentages
    aug = iaa.Crop(percent=((0, 0.1), 0, 0, 0), keep_size=False)
    seen = [0, 0, 0, 0, 0]
    for _ in sm.xrange(500):
        observed = aug.augment_image(np.zeros((40, 40), dtype=np.uint8))
        n_cropped = 40 - observed.shape[0]
        seen[n_cropped] += 1
    # note that we cant just check for 100-50 < x < 100+50 here. The first and last value (0px
    # and 4px) have half the probability of occuring compared to the other values.
    # E.g. 0px is cropped if sampled p falls in range [0, 0.125). 1px is cropped if sampled p
    # falls in range [0.125, 0.375].
    assert all([v > 30 for v in seen])

    aug = iaa.Crop(percent=(0, (0, 0.1), 0, 0), keep_size=False)
    seen = [0, 0, 0, 0, 0]
    for _ in sm.xrange(500):
        observed = aug.augment_image(np.zeros((40, 40), dtype=np.uint8) + 255)
        n_cropped = 40 - observed.shape[1]
        seen[n_cropped] += 1
    assert all([v > 30 for v in seen])

    # test crop by list of percentages
    aug = iaa.Crop(percent=([0.0, 0.1], 0, 0, 0), keep_size=False)
    seen = [0, 0, 0, 0, 0]
    for _ in sm.xrange(500):
        observed = aug.augment_image(np.zeros((40, 40), dtype=np.uint8) + 255)
        n_cropped = 40 - observed.shape[0]
        seen[n_cropped] += 1
    assert 250 - 50 < seen[0] < 250 + 50
    assert seen[1] == 0
    assert seen[2] == 0
    assert seen[3] == 0
    assert 250 - 50 < seen[4] < 250 + 50

    aug = iaa.Crop(percent=(0, [0.0, 0.1], 0, 0), keep_size=False)
    seen = [0, 0, 0, 0, 0]
    for _ in sm.xrange(500):
        observed = aug.augment_image(np.zeros((40, 40), dtype=np.uint8) + 255)
        n_cropped = 40 - observed.shape[1]
        seen[n_cropped] += 1
    assert 250 - 50 < seen[0] < 250 + 50
    assert seen[1] == 0
    assert seen[2] == 0
    assert seen[3] == 0
    assert 250 - 50 < seen[4] < 250 + 50


def test_PadToFixedSize():
    reseed()

    img = np.uint8([[255]])
    img3d = img[:, :, np.newaxis]
    img3d_rgb = np.tile(img3d, (1, 1, 3))

    # basic functionality
    aug = iaa.PadToFixedSize(height=5, width=5)
    observed = aug.augment_image(img)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (5, 5)

    observed = aug.augment_image(img3d)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (5, 5, 1)

    observed = aug.augment_image(img3d_rgb)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (5, 5, 3)

    # test float32, float64, int32
    for dtype in [np.float32, np.float64, np.int32]:
        aug = iaa.PadToFixedSize(height=5, width=5)
        observed = aug.augment_image(img.astype(dtype))
        assert observed.dtype.type == dtype
        assert observed.shape == (5, 5)

    # change only one side when other side has already desired size
    aug = iaa.PadToFixedSize(height=5, width=5)
    observed = aug.augment_image(np.zeros((1, 5, 3), dtype=np.uint8))
    assert observed.dtype.type == np.uint8
    assert observed.shape == (5, 5, 3)

    aug = iaa.PadToFixedSize(height=5, width=5)
    observed = aug.augment_image(np.zeros((5, 1, 3), dtype=np.uint8))
    assert observed.dtype.type == np.uint8
    assert observed.shape == (5, 5, 3)

    # change no side when all sides have exactly desired size
    img5x5 = np.zeros((5, 5, 3), dtype=np.uint8)
    img5x5[2, 2, :] = 255
    aug = iaa.PadToFixedSize(height=5, width=5)
    observed = aug.augment_image(img5x5)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (5, 5, 3)
    assert np.array_equal(observed, img5x5)

    # change no side when all sides have larger than desired size
    img6x6 = np.zeros((6, 6, 3), dtype=np.uint8)
    img6x6[3, 3, :] = 255
    aug = iaa.PadToFixedSize(height=5, width=5)
    observed = aug.augment_image(img6x6)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (6, 6, 3)
    assert np.array_equal(observed, img6x6)

    # make sure that pad mode is recognized
    aug = iaa.PadToFixedSize(height=4, width=4, pad_mode="edge")
    aug.position = (iap.Deterministic(0.5), iap.Deterministic(0.5))
    img2x2 = np.uint8([
        [50, 100],
        [150, 200]
    ])
    expected = np.uint8([
        [50, 50, 100, 100],
        [50, 50, 100, 100],
        [150, 150, 200, 200],
        [150, 150, 200, 200]
    ])
    observed = aug.augment_image(img2x2)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (4, 4)
    assert np.array_equal(observed, expected)

    # explicit non-center position test
    aug = iaa.PadToFixedSize(height=3, width=3, pad_mode="constant", pad_cval=128)
    aug.position = (iap.Deterministic(0.0), iap.Deterministic(0.0))
    img1x1 = np.uint8([[255]])
    observed = aug.augment_image(img1x1)
    expected = np.uint8([
        [128, 128, 128],
        [128, 128, 128],
        [128, 128, 255]
    ])
    assert observed.dtype.type == np.uint8
    assert observed.shape == (3, 3)
    assert np.array_equal(observed, expected)

    aug = iaa.PadToFixedSize(height=3, width=3, pad_mode="constant", pad_cval=128)
    aug.position = (iap.Deterministic(1.0), iap.Deterministic(1.0))
    img1x1 = np.uint8([[255]])
    observed = aug.augment_image(img1x1)
    expected = np.uint8([
        [255, 128, 128],
        [128, 128, 128],
        [128, 128, 128]
    ])
    assert observed.dtype.type == np.uint8
    assert observed.shape == (3, 3)
    assert np.array_equal(observed, expected)

    # basic keypoint test
    kpsoi = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(3, 3))
    aug = iaa.PadToFixedSize(height=4, width=4, pad_mode="edge")
    aug.position = (iap.Deterministic(0.5), iap.Deterministic(0.5))
    observed = aug.augment_keypoints([kpsoi])
    expected = ia.KeypointsOnImage([ia.Keypoint(x=2, y=2)], shape=(4, 4))
    assert observed[0].shape == expected.shape
    assert keypoints_equal(observed, [expected])

    # keypoint test with shape not being changed
    kpsoi = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(3, 3))
    aug = iaa.PadToFixedSize(height=3, width=3, pad_mode="edge")
    aug.position = (iap.Deterministic(0.5), iap.Deterministic(0.5))
    observed = aug.augment_keypoints([kpsoi])
    expected = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(3, 3))
    assert observed[0].shape == expected.shape
    assert keypoints_equal(observed, [expected])

    # keypoint test with explicit non-center position
    kpsoi = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(3, 3))
    aug = iaa.PadToFixedSize(height=4, width=4, pad_mode="edge")
    aug.position = (iap.Deterministic(0.0), iap.Deterministic(0.0))
    observed = aug.augment_keypoints([kpsoi])
    expected = ia.KeypointsOnImage([ia.Keypoint(x=2, y=2)], shape=(4, 4))
    assert observed[0].shape == expected.shape
    assert keypoints_equal(observed, [expected])

    kpsoi = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(3, 3))
    aug = iaa.PadToFixedSize(height=4, width=4, pad_mode="edge")
    aug.position = (iap.Deterministic(1.0), iap.Deterministic(1.0))
    observed = aug.augment_keypoints([kpsoi])
    expected = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(4, 4))
    assert observed[0].shape == expected.shape
    assert keypoints_equal(observed, [expected])

    # basic heatmaps test
    heatmaps = ia.HeatmapsOnImage(np.zeros((1, 1, 1), dtype=np.float32) + 1.0, shape=(1, 1, 3))
    aug = iaa.PadToFixedSize(height=3, width=3, pad_mode="edge")  # pad_mode should be ignored for heatmaps
    aug.position = (iap.Deterministic(0.5), iap.Deterministic(0.5))
    observed = aug.augment_heatmaps([heatmaps])[0]
    expected = np.float32([
        [0, 0, 0],
        [0, 1.0, 0],
        [0, 0, 0]
    ])
    expected = expected[..., np.newaxis]
    assert observed.shape == (3, 3, 3)
    assert np.allclose(observed.arr_0to1, expected)

    # heatmaps with size unequal to image
    heatmaps = ia.HeatmapsOnImage(np.zeros((15, 15, 1), dtype=np.float32) + 1.0, shape=(30, 30, 3))
    aug = iaa.PadToFixedSize(height=32, width=32, pad_mode="edge")  # pad_mode should be ignored for heatmaps
    aug.position = (iap.Deterministic(0.0), iap.Deterministic(0.0))
    observed = aug.augment_heatmaps([heatmaps])[0]
    expected = np.zeros((16, 16, 1), dtype=np.float32) + 1.0
    expected[:, 0, 0] = 0.0
    expected[0, :, 0] = 0.0
    assert observed.shape == (32, 32, 3)
    assert np.allclose(observed.arr_0to1, expected)


def test_CropToFixedSize():
    reseed()

    img = np.uint8([
        [128, 129, 130],
        [131, 132, 133],
        [134, 135, 136]
    ])
    img3d = img[:, :, np.newaxis]
    img3d_rgb = np.tile(img3d, (1, 1, 3))

    # basic functionality
    aug = iaa.CropToFixedSize(height=1, width=1)
    observed = aug.augment_image(img)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (1, 1)

    observed = aug.augment_image(img3d)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (1, 1, 1)

    observed = aug.augment_image(img3d_rgb)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (1, 1, 3)

    # test float32, float64, int32
    for dtype in [np.float32, np.float64, np.int32]:
        aug = iaa.CropToFixedSize(height=1, width=1)
        observed = aug.augment_image(img.astype(dtype))
        assert observed.dtype.type == dtype
        assert observed.shape == (1, 1)

    # change only one side when other side has already desired size
    aug = iaa.CropToFixedSize(height=3, width=5)
    observed = aug.augment_image(np.zeros((3, 5, 3), dtype=np.uint8))
    assert observed.dtype.type == np.uint8
    assert observed.shape == (3, 5, 3)

    aug = iaa.CropToFixedSize(height=5, width=3)
    observed = aug.augment_image(np.zeros((5, 3, 3), dtype=np.uint8))
    assert observed.dtype.type == np.uint8
    assert observed.shape == (5, 3, 3)

    # change no side when all sides have exactly desired size
    img5x5 = np.zeros((5, 5, 3), dtype=np.uint8)
    img5x5[2, 2, :] = 255
    aug = iaa.CropToFixedSize(height=5, width=5)
    observed = aug.augment_image(img5x5)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (5, 5, 3)
    assert np.array_equal(observed, img5x5)

    # change no side when all sides have smaller than desired size
    img4x4 = np.zeros((4, 4, 3), dtype=np.uint8)
    img4x4[2, 2, :] = 255
    aug = iaa.CropToFixedSize(height=5, width=5)
    observed = aug.augment_image(img4x4)
    assert observed.dtype.type == np.uint8
    assert observed.shape == (4, 4, 3)
    assert np.array_equal(observed, img4x4)

    # explicit non-center position test
    aug = iaa.CropToFixedSize(height=3, width=3)
    aug.position = (iap.Deterministic(0.0), iap.Deterministic(0.0))
    img5x5 = np.arange(25, dtype=np.uint8).reshape((5, 5))
    observed = aug.augment_image(img5x5)
    expected = img5x5[2:, 2:]
    assert observed.dtype.type == np.uint8
    assert observed.shape == (3, 3)
    assert np.array_equal(observed, expected)

    aug = iaa.CropToFixedSize(height=3, width=3)
    aug.position = (iap.Deterministic(1.0), iap.Deterministic(1.0))
    img5x5 = np.arange(25, dtype=np.uint8).reshape((5, 5))
    observed = aug.augment_image(img5x5)
    expected = img5x5[:3, :3]
    assert observed.dtype.type == np.uint8
    assert observed.shape == (3, 3)
    assert np.array_equal(observed, expected)

    # basic keypoint test
    kpsoi = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(3, 3))
    aug = iaa.CropToFixedSize(height=1, width=1)
    aug.position = (iap.Deterministic(0.5), iap.Deterministic(0.5))
    observed = aug.augment_keypoints([kpsoi])
    expected = ia.KeypointsOnImage([ia.Keypoint(x=0, y=0)], shape=(1, 1))
    assert observed[0].shape == expected.shape
    assert keypoints_equal(observed, [expected])

    # keypoint test with shape not being changed
    kpsoi = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(3, 3))
    aug = iaa.CropToFixedSize(height=3, width=3)
    aug.position = (iap.Deterministic(0.5), iap.Deterministic(0.5))
    observed = aug.augment_keypoints([kpsoi])
    expected = ia.KeypointsOnImage([ia.Keypoint(x=1, y=1)], shape=(3, 3))
    assert observed[0].shape == expected.shape
    assert keypoints_equal(observed, [expected])

    # keypoint test with explicit non-center position
    kpsoi = ia.KeypointsOnImage([ia.Keypoint(x=2, y=2)], shape=(5, 5))
    aug = iaa.CropToFixedSize(height=3, width=3)
    aug.position = (iap.Deterministic(0.0), iap.Deterministic(0.0))
    observed = aug.augment_keypoints([kpsoi])
    expected = ia.KeypointsOnImage([ia.Keypoint(x=0, y=0)], shape=(3, 3))
    assert observed[0].shape == expected.shape
    assert keypoints_equal(observed, [expected])

    kpsoi = ia.KeypointsOnImage([ia.Keypoint(x=2, y=2)], shape=(5, 5))
    aug = iaa.CropToFixedSize(height=3, width=3)
    aug.position = (iap.Deterministic(1.0), iap.Deterministic(1.0))
    observed = aug.augment_keypoints([kpsoi])
    expected = ia.KeypointsOnImage([ia.Keypoint(x=2, y=2)], shape=(3, 3))
    assert observed[0].shape == expected.shape
    assert keypoints_equal(observed, [expected])

    # basic heatmaps test
    heatmaps = ia.HeatmapsOnImage(np.zeros((5, 5, 1), dtype=np.float32) + 1.0, shape=(5, 5, 3))
    aug = iaa.CropToFixedSize(height=3, width=3)
    aug.position = (iap.Deterministic(0.5), iap.Deterministic(0.5))
    observed = aug.augment_heatmaps([heatmaps])[0]
    expected = np.zeros((3, 3, 1), dtype=np.float32) + 1.0
    assert observed.shape == (3, 3, 3)
    assert np.allclose(observed.arr_0to1, expected)

    # heatmaps with size unequal to image
    heatmaps = ia.HeatmapsOnImage(np.zeros((17, 17, 1), dtype=np.float32) + 1.0, shape=(34, 34, 3))
    aug = iaa.CropToFixedSize(height=32, width=32)
    aug.position = (iap.Deterministic(0.0), iap.Deterministic(0.0))
    observed = aug.augment_heatmaps([heatmaps])[0]
    expected = np.zeros((16, 16, 1), dtype=np.float32) + 1.0
    assert observed.shape == (32, 32, 3)
    assert np.allclose(observed.arr_0to1, expected)


if __name__ == "__main__":
    main()
