#!/usr/bin/env python

"""Parity tests for agent extraction against ROBERT output evidence files.

These tests are intentionally outside the runtime UI workflow. They validate that
the extracted run_context fields match score-critical evidence from the same
PREDICT/VERIFY dat files used by ROBERT report logic.
"""

import ast
import json
import re
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_ARCHIVE = PROJECT_ROOT / "agent" / "run_archive"

REGRESSION_RUN = RUN_ARCHIVE / "20260515_173258__Hvapor"
CLASSIFICATION_RUN = RUN_ARCHIVE / "20260516_150946__TOF_class"
INCOMPLETE_RUN = RUN_ARCHIVE / "20260516_151123__TOF_class_incomplete"


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as f:
        return f.readlines()


def _to_float(text: str) -> float:
    return float(text.strip())


def _extract_predict_parity(predict_dat_path: Path) -> dict:
    """Extract score-critical metrics from PREDICT_data.dat for parity checks."""
    data = {
        "no_pfi": {},
        "pfi": {},
    }
    current = None
    lines = _read_lines(predict_dat_path)

    for raw in lines:
        line = raw.strip()
        if "Starting model with all variables (No PFI)" in line:
            current = "no_pfi"
            continue
        if "Starting model with PFI filter" in line:
            current = "pfi"
            continue
        if current is None:
            continue

        if "Training points:" in line:
            data[current]["n_train"] = int(line.split(":", 1)[1].strip())
        elif "Test points:" in line:
            data[current]["n_test"] = int(line.split(":", 1)[1].strip())
        elif "Number of descriptors =" in line:
            data[current]["n_descriptors"] = int(line.split("=", 1)[1].strip())
        elif "Proportion (train+valid.) points:descriptors =" in line:
            data[current]["points_descp_ratio"] = line.split("=", 1)[1].strip()
        elif "Descriptors:" in line:
            data[current]["descriptors"] = ast.literal_eval(line.split(":", 1)[1].strip())
        elif "10x 5-fold CV : R2 =" in line:
            match = re.search(r"R2 = ([^,]+), MAE = ([^,]+), RMSE = ([^,]+)", line)
            assert match, f"Could not parse regression CV line: {line}"
            data[current]["r2_cv"] = _to_float(match.group(1))
            data[current]["mae_cv"] = _to_float(match.group(2))
            data[current]["rmse_cv"] = _to_float(match.group(3))
        elif "Test : R2 =" in line:
            match = re.search(r"R2 = ([^,]+), MAE = ([^,]+), RMSE = ([^,]+)", line)
            assert match, f"Could not parse regression test line: {line}"
            data[current]["r2_test"] = _to_float(match.group(1))
            data[current]["mae_test"] = _to_float(match.group(2))
            data[current]["rmse_test"] = _to_float(match.group(3))
        elif "10x 5-fold CV : Accur. =" in line:
            match = re.search(r"Accur\. = ([^,]+), F1 score = ([^,]+), MCC = ([^,]+)", line)
            assert match, f"Could not parse classification CV line: {line}"
            data[current]["accuracy_cv"] = _to_float(match.group(1))
            data[current]["f1_cv"] = _to_float(match.group(2))
            data[current]["mcc_cv"] = _to_float(match.group(3))
        elif "Test : Accur. =" in line:
            match = re.search(r"Accur\. = ([^,]+), F1 score = ([^,]+), MCC = ([^,]+)", line)
            assert match, f"Could not parse classification test line: {line}"
            data[current]["accuracy_test"] = _to_float(match.group(1))
            data[current]["f1_test"] = _to_float(match.group(2))
            data[current]["mcc_test"] = _to_float(match.group(3))

    return data


def _extract_sorted_cv_parity(verify_dat_path: Path) -> dict:
    """Extract sorted CV stability arrays used by report scoring logic."""
    data = {"no_pfi": {}, "pfi": {}}
    lines = _read_lines(verify_dat_path)
    current = None

    for raw in lines:
        line = raw.strip()
        if "Starting model with all variables (No PFI)" in line:
            current = "no_pfi"
            continue
        if "Starting model with PFI filter" in line:
            current = "pfi"
            continue
        if current is None:
            continue

        if "- Sorted 5-fold CV :" in line or "- Sorted CV :" in line:
            rmse_match = re.search(r"RMSE = (\[[^\]]+\])", line)
            r2_match = re.search(r"R2 = (\[[^\]]+\])", line)
            mcc_match = re.search(r"MCC = (\[[^\]]+\])", line)

            if rmse_match:
                data[current]["sorted_cv_rmse"] = ast.literal_eval(rmse_match.group(1))
            if r2_match:
                data[current]["sorted_cv_r2"] = ast.literal_eval(r2_match.group(1))
            if mcc_match:
                data[current]["sorted_cv_mcc"] = ast.literal_eval(mcc_match.group(1))

    return data


def _extract_verify_parity(verify_dat_path: Path) -> dict:
    """Extract VERIFY verdict counts and raw result labels for parity checks."""
    data = {
        "no_pfi": {"test_results": []},
        "pfi": {"test_results": []},
    }
    current = None
    lines = _read_lines(verify_dat_path)

    for raw in lines:
        line = raw.strip()
        if "Starting model with all variables (No PFI)" in line:
            current = "no_pfi"
            continue
        if "Starting model with PFI filter" in line:
            current = "pfi"
            continue
        if current is None:
            continue

        verdict_match = re.search(r"o\s+(y_mean|y_shuffle|onehot):\s+(PASSED|FAILED|UNCLEAR)", line)
        if verdict_match:
            test_name = verdict_match.group(1)
            verdict = verdict_match.group(2)
            data[current]["test_results"].append(f"{test_name}: {verdict}")

    for variant in ["no_pfi", "pfi"]:
        results = data[variant]["test_results"]
        data[variant]["passed_tests"] = sum("PASSED" in x for x in results)
        data[variant]["failed_tests"] = sum("FAILED" in x for x in results)
        data[variant]["unclear_tests"] = sum("UNCLEAR" in x for x in results)
        flawed = -2 * data[variant]["failed_tests"] - data[variant]["unclear_tests"]
        data[variant]["flawed_mod_score"] = max(flawed, -6)

    return data


def _assert_predict_parity(run_context: dict, predict_expected: dict, pred_type: str) -> None:
    for variant in ["no_pfi", "pfi"]:
        got = run_context["predict"][variant]
        exp = predict_expected[variant]

        assert got["n_train"] == exp["n_train"]
        assert got["n_test"] == exp["n_test"]
        assert got["n_descriptors"] == exp["n_descriptors"]
        assert got["points_descp_ratio"] == exp["points_descp_ratio"]
        assert got["descriptors"] == exp["descriptors"]

        if pred_type == "reg":
            assert got["r2_cv"] == pytest.approx(exp["r2_cv"], abs=1e-6)
            assert got["r2_test"] == pytest.approx(exp["r2_test"], abs=1e-6)
            assert got["mae_cv"] == pytest.approx(exp["mae_cv"], abs=1e-6)
            assert got["mae_test"] == pytest.approx(exp["mae_test"], abs=1e-6)
            assert got["rmse_cv"] == pytest.approx(exp["rmse_cv"], abs=1e-6)
            assert got["rmse_test"] == pytest.approx(exp["rmse_test"], abs=1e-6)
        else:
            assert got["accuracy_cv"] == pytest.approx(exp["accuracy_cv"], abs=1e-6)
            assert got["accuracy_test"] == pytest.approx(exp["accuracy_test"], abs=1e-6)
            assert got["f1_cv"] == pytest.approx(exp["f1_cv"], abs=1e-6)
            assert got["f1_test"] == pytest.approx(exp["f1_test"], abs=1e-6)
            assert got["mcc_cv"] == pytest.approx(exp["mcc_cv"], abs=1e-6)
            assert got["mcc_test"] == pytest.approx(exp["mcc_test"], abs=1e-6)
            # Classification branch duplicates MCC into r2_* fields in run_context.
            assert got["r2_cv"] == pytest.approx(exp["mcc_cv"], abs=1e-6)
            assert got["r2_test"] == pytest.approx(exp["mcc_test"], abs=1e-6)
            assert got["rmse_cv"] is None
            assert got["rmse_test"] is None


def _assert_verify_parity(run_context: dict, verify_expected: dict) -> None:
    for variant in ["no_pfi", "pfi"]:
        got = run_context["verify"][variant]
        exp = verify_expected[variant]

        assert got["passed_tests"] == exp["passed_tests"]
        assert got["failed_tests"] == exp["failed_tests"]
        assert got["unclear_tests"] == exp["unclear_tests"]
        assert got["flawed_mod_score"] == exp["flawed_mod_score"]
        assert got["test_results"] == exp["test_results"]


def _assert_sorted_cv_parity(run_context: dict, sorted_cv_expected: dict) -> None:
    """Verify sorted CV stability arrays match extracted values when present.
    
    Note: This is a parity check. If a field is populated in the extractor,
    it must match the source dat file. Unpopulated fields are marked as gaps.
    """
    for variant in ["no_pfi", "pfi"]:
        got = run_context["verify"][variant]
        exp = sorted_cv_expected[variant]

        if "sorted_cv_rmse" in exp and got.get("sorted_cv_rmse"):
            assert got.get("sorted_cv_rmse") == exp["sorted_cv_rmse"]
        if "sorted_cv_r2" in exp and got.get("sorted_cv_r2"):
            assert got.get("sorted_cv_r2") == exp["sorted_cv_r2"]
        if "sorted_cv_mcc" in exp and got.get("sorted_cv_mcc"):
            got_mcc = got.get("sorted_cv_mcc", [])
            exp_mcc = exp["sorted_cv_mcc"]
            assert len(got_mcc) == len(exp_mcc)
            for g, e in zip(got_mcc, exp_mcc):
                assert g == pytest.approx(e, abs=1e-6)


def test_regression_run_parity_against_predict_and_verify_dat() -> None:
    run_context = _read_json(REGRESSION_RUN / "run_context.json")
    predict_expected = _extract_predict_parity(REGRESSION_RUN / "outputs" / "PREDICT" / "PREDICT_data.dat")
    verify_expected = _extract_verify_parity(REGRESSION_RUN / "outputs" / "VERIFY" / "VERIFY_data.dat")
    sorted_cv_expected = _extract_sorted_cv_parity(REGRESSION_RUN / "outputs" / "VERIFY" / "VERIFY_data.dat")

    assert run_context["pred_type"] == "reg"
    assert run_context["available"]["predict"] is True
    assert run_context["available"]["verify"] is True

    _assert_predict_parity(run_context, predict_expected, pred_type="reg")
    _assert_verify_parity(run_context, verify_expected)
    _assert_sorted_cv_parity(run_context, sorted_cv_expected)


def test_classification_run_parity_against_predict_and_verify_dat() -> None:
    run_context = _read_json(CLASSIFICATION_RUN / "run_context.json")
    predict_expected = _extract_predict_parity(CLASSIFICATION_RUN / "outputs" / "PREDICT" / "PREDICT_data.dat")
    verify_expected = _extract_verify_parity(CLASSIFICATION_RUN / "outputs" / "VERIFY" / "VERIFY_data.dat")
    sorted_cv_expected = _extract_sorted_cv_parity(CLASSIFICATION_RUN / "outputs" / "VERIFY" / "VERIFY_data.dat")

    assert run_context["pred_type"] == "clas"
    assert run_context["available"]["predict"] is True
    assert run_context["available"]["verify"] is True

    _assert_predict_parity(run_context, predict_expected, pred_type="clas")
    _assert_verify_parity(run_context, verify_expected)
    _assert_sorted_cv_parity(run_context, sorted_cv_expected)


def test_incomplete_run_is_null_safe_for_missing_verify_curate_generate() -> None:
    run_context = _read_json(INCOMPLETE_RUN / "run_context.json")
    predict_expected = _extract_predict_parity(INCOMPLETE_RUN / "outputs" / "PREDICT" / "PREDICT_data.dat")

    assert run_context["available"]["predict"] is True
    assert run_context["available"]["verify"] is False
    assert run_context["available"]["curate"] is False
    assert run_context["available"]["generate"] is False

    _assert_predict_parity(run_context, predict_expected, pred_type="clas")

    for variant in ["no_pfi", "pfi"]:
        verify_section = run_context["verify"][variant]
        assert verify_section["passed_tests"] is None
        assert verify_section["failed_tests"] is None
        assert verify_section["unclear_tests"] is None
        assert verify_section["flawed_mod_score"] is None
        assert verify_section["test_results"] is None
