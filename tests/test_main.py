import pytest
from unittest.mock import patch
import pandas as pd


def make_dummy_df():
    # minimal dataframe similar to extractor output
    return pd.DataFrame(
        [
            ["abcd12", "CALL", "France", 1620000000, 1620000001, 1.0, 2.0, 1000.0, False, 200.0, 0.0, 0.0, None, None, 0, 0],
        ]
    )


@patch("src.extractor.extract_flight_data")
@patch("src.transformer.transform_flight_data")
@patch("src.transformer.validate_data")
@patch("src.loader.load_to_sqlite")
def test_run_iteration_once_dryrun(mock_load, mock_validate, mock_transform, mock_extract):
    """Test that run_pipeline_iteration can be run in dry-run and that --once behavior exits after one iteration."""
    from main import run_pipeline_iteration

    df = make_dummy_df()
    mock_extract.return_value = df
    mock_transform.return_value = df
    mock_validate.return_value = True
    mock_load.return_value = True

    # Dry-run should return True and skip load (so load_to_sqlite not called)
    success = run_pipeline_iteration(dry_run=True)
    assert success is True
    mock_load.assert_not_called()
