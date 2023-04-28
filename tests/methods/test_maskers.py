import numpy as np
import pytest
from dianna.utils.maskers import generate_channel_masks
from dianna.utils.maskers import generate_masks
from dianna.utils.maskers import mask_data


def test_mask_has_correct_shape_univariate():
    """Test masked data has the correct shape for a univariate input."""
    input_data = _get_univariate_input_data()
    number_of_masks = 5

    result = _call_masking_function(input_data, number_of_masks=number_of_masks)

    assert result.shape == tuple([number_of_masks] + list(input_data.shape))


def test_mask_has_correct_shape_multivariate():
    """Test masked data has the correct shape for a multivariate input."""
    input_data = _get_multivariate_input_data()
    number_of_masks = 5

    result = _call_masking_function(input_data, number_of_masks=number_of_masks)

    assert result.shape == tuple([number_of_masks] + list(input_data.shape))


@pytest.mark.parametrize("p_keep_and_expected_rate", [
    (0.1, 0.1),  # Mask all but one
    (0.1, 0.1),
    (0.3, 0.3),
    (0.5, 0.5),
    (0.667, 0.7),
    (0.99, 0.9),  # Mask only 1
])
def test_mask_contains_correct_number_of_unmasked_parts(p_keep_and_expected_rate):
    """Number of unmasked parts should be conforming the given p_keep."""
    p_keep, expected_rate = p_keep_and_expected_rate
    input_data = _get_univariate_input_data()

    result = _call_masking_function(input_data, p_keep=p_keep)

    assert np.sum(result == input_data) / np.product(result.shape) == expected_rate


def test_mask_contains_correct_parts_are_mean_masked():
    """All parts that are masked should now contain the mean of the input."""
    input_data = _get_univariate_input_data()
    mean = np.mean(input_data)

    result = _call_masking_function(input_data, mask_type='mean')

    masked_parts = result[(result != input_data)]
    assert np.alltrue(masked_parts == mean), f'All elements in {masked_parts} should have value {mean}'


def _get_univariate_input_data() -> np.array:
    """Get some univariate test data."""
    return np.zeros((10, 1)) + np.arange(10).reshape(10, 1)


def _get_multivariate_input_data(number_of_channels: int = 6) -> np.array:
    """Get some multivariate test data."""
    return np.row_stack([np.zeros((10, number_of_channels)), np.ones((10, number_of_channels))])


def _call_masking_function(input_data, number_of_masks=5, p_keep=.3, mask_type='mean'):
    """Helper function with some defaults to call the code under test."""
    masks = generate_masks(input_data, number_of_masks, p_keep=p_keep)
    return mask_data(input_data, masks, mask_type=mask_type)


def test_channel_mask_has_correct_shape_multivariate():
    """Tests the output has the correct shape."""
    number_of_masks = 15
    input_data = _get_multivariate_input_data()

    result = generate_channel_masks(input_data, number_of_masks, 0.5)

    assert result.shape == tuple([number_of_masks] + list(input_data.shape))


def test_channel_mask_has_does_not_contain_conflicting_values():
    """Tests that only complete channels are masked."""
    number_of_masks = 15
    input_data = _get_multivariate_input_data()

    result = generate_channel_masks(input_data, number_of_masks, 0.5)

    unexpected_results = []
    for mask_i, mask in enumerate(result):
        for channel_i in range(mask.shape[-1]):
            channel = mask[:, channel_i]
            value = channel[0]
            if (not value) in channel:
                unexpected_results.append(
                    f'Mask {mask_i} contains conflicting values in channel {channel_i}. Channel: {channel}')
    assert not unexpected_results


def test_channel_mask_masks_correct_number_of_cells():
    """Tests whether the correct fraction of cells is masked."""
    number_of_masks = 1
    input_data = _get_multivariate_input_data(number_of_channels=10)
    p_keep = 0.3

    result = generate_channel_masks(input_data, number_of_masks, p_keep)

    assert result.sum() / np.product(result.shape) == p_keep


def test_masking_has_correct_shape_multivariate():
    """Test for the correct output shape for the general masking function."""
    number_of_masks = 15
    input_data = _get_multivariate_input_data()

    result = generate_masks(input_data, number_of_masks, 0.5)

    assert result.shape == tuple([number_of_masks] + list(input_data.shape))


def test_masking_univariate_leaves_anything_unmasked():
    """Tests that something remains unmasked and some parts are masked for the univariate case."""
    number_of_masks = 1
    input_data = _get_univariate_input_data()

    result = generate_masks(input_data, number_of_masks, 0.5)

    assert np.any(result)
    assert np.any(~result)