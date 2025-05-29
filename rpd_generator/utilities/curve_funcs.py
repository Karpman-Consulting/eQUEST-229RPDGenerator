from typing import Dict, List

from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BDL_CurveFitKeywords = BDLEnums.bdl_enums["CurveFitKeywords"]
BDL_CurveFitInputTypes = BDLEnums.bdl_enums["CurveFitInputTypes"]
BDL_CurveFitTypes = BDLEnums.bdl_enums["CurveFitTypes"]


def calculate_bi_linear(
    curve_coeffs: List[float], x: float, y: float, min_val: float, max_val: float
) -> float:
    """
    Computes the output of a bi-linear equation using the given coefficients and two independent variables.

    The function evaluates the equation:

        Z = a + b*x + c*y + d*x*y

    where `curve_coeffs` is a list of four coefficients corresponding to:
    - `a` (index 0): Constant term
    - `b` (index 1): Linear term for `x`
    - `c` (index 2): Linear term for `y`
    - `d` (index 3): Interaction term (`x*y`)

    The computed value `Z` is then constrained within the range `[min_val, max_val]`.

    Parameters:
        curve_coeffs (List[float]): A list of four coefficients `[a, b, c, d]` defining the bi-linear equation.
        x (float): The first independent variable.
        y (float): The second independent variable.
        min_val (float): The minimum allowable value for the computed result.
        max_val (float): The maximum allowable value for the computed result.

    Returns:
        float: The computed `Z` value, constrained within `[min_val, max_val]`.
    """
    z = (
        curve_coeffs[0]
        + curve_coeffs[1] * x
        + curve_coeffs[2] * y
        + curve_coeffs[3] * x * y
    )

    # Ensure z is within the range [min_val, max_val]
    z = max(min_val, min(z, max_val))

    return z


def calculate_bi_quadratic(
    curve_coeffs: List[float], x: float, y: float, min_val: float, max_val: float
) -> float:
    """
    Computes the output of a bi-quadratic equation using the given coefficients and two independent variables.

    The function evaluates the equation:

        Z = a + b*x + c*x² + d*y + e*y² + f*x*y

    where `curve_coeffs` is a list of six coefficients corresponding to:
    - `a` (index 0): Constant term
    - `b` (index 1): Linear term for `x`
    - `c` (index 2): Quadratic term for `x`
    - `d` (index 3): Linear term for `y`
    - `e` (index 4): Quadratic term for `y`
    - `f` (index 5): Interaction term (`x*y`)

    The computed value `Z` is then constrained within the range `[min_val, max_val]`.

    This function is designed to process eQuest BI-QUADRATIC curves.

    Parameters:
        curve_coeffs (List[float]): A list of six coefficients `[a, b, c, d, e, f]` defining the bi-quadratic equation.
        x (float): The first independent variable.
        y (float): The second independent variable.
        min_val (float): The minimum allowable value for the computed result.
        max_val (float): The maximum allowable value for the computed result.

    Returns:
        float: The computed `Z` value, constrained within `[min_val, max_val]`.
    """
    z = (
        curve_coeffs[0]
        + curve_coeffs[1] * x
        + curve_coeffs[2] * x**2
        + curve_coeffs[3] * y
        + curve_coeffs[4] * y**2
        + curve_coeffs[5] * x * y
    )

    # Ensure z is within the range [min_val, max_val]
    z = max(min_val, min(z, max_val))

    return z


def calculate_cubic(
    curve_coeffs: List[float], x: float, min_val: float, max_val: float
) -> float:
    """
    Computes the output of a cubic equation using the given coefficients and an independent variable.

    The function evaluates the equation:

        Z = a + b*x + c*x² + d*x³

    where `curve_coeffs` is a list of four coefficients corresponding to:
    - `a` (index 0): Constant term
    - `b` (index 1): Linear term for `x`
    - `c` (index 2): Quadratic term for `x`
    - `d` (index 3): Cubic term for `x`

    The computed value `Z` is then constrained within the range `[min_val, max_val]`.

    Parameters:
        curve_coeffs (List[float]): A list of four coefficients `[a, b, c, d]` defining the cubic equation.
        x (float): The independent variable.
        min_val (float): The minimum allowable value for the computed result.
        max_val (float): The maximum allowable value for the computed result.

    Returns:
        float: The computed `Z` value, constrained within `[min_val, max_val]`.
    """
    # Extend the list with zeros if it has fewer than 4 coefficients
    coeffs = curve_coeffs + [0.0] * (4 - len(curve_coeffs))

    z = coeffs[0] + coeffs[1] * x + coeffs[2] * x**2 + coeffs[3] * x**3

    # Ensure z is within the range [min_val, max_val]
    z = max(min_val, min(z, max_val))

    return z


def calculate_quadratic(
    curve_coeffs: List[float], x: float, min_val: float, max_val: float
) -> float:
    """
    Computes the output of a quadratic equation using the given coefficients and an independent variable.

    The function evaluates the equation:

        Z = a + b*x + c*x²

    where `curve_coeffs` is a list of three coefficients corresponding to:
    - `a` (index 0): Constant term
    - `b` (index 1): Linear term for `x`
    - `c` (index 2): Quadratic term for `x`

    The computed value `Z` is then constrained within the range `[min_val, max_val]`.

    Parameters:
        curve_coeffs (List[float]): A list of three coefficients `[a, b, c]` defining the quadratic equation.
        x (float): The independent variable.
        min_val (float): The minimum allowable value for the computed result.
        max_val (float): The maximum allowable value for the computed result.

    Returns:
        float: The computed `Z` value, constrained within `[min_val, max_val]`.
    """
    z = curve_coeffs[0] + curve_coeffs[1] * x + curve_coeffs[2] * x**2

    # Ensure z is within the range [min_val, max_val]
    z = max(min_val, min(z, max_val))

    return z


CURVE_FUNCTION_MAP = {
    BDL_CurveFitTypes.LINEAR: calculate_bi_linear,
    BDL_CurveFitTypes.QUADRATIC: calculate_quadratic,
    BDL_CurveFitTypes.QUADRATIC_T: calculate_quadratic,
    BDL_CurveFitTypes.QUADRATIC_DT: calculate_quadratic,
    BDL_CurveFitTypes.CUBIC: calculate_cubic,
    BDL_CurveFitTypes.CUBIC_T: calculate_cubic,
    BDL_CurveFitTypes.BI_LINEAR: calculate_bi_linear,
    BDL_CurveFitTypes.BI_LINEAR_T: calculate_bi_linear,
    BDL_CurveFitTypes.BI_QUADRATIC: calculate_bi_quadratic,
    BDL_CurveFitTypes.BI_QUADRATIC_T: calculate_bi_quadratic,
    BDL_CurveFitTypes.BI_QUADRATIC_DT_T: calculate_bi_quadratic,
    BDL_CurveFitTypes.BI_QUADRATIC_T_RATIO: calculate_bi_quadratic,
    BDL_CurveFitTypes.BI_QUADRATIC_RATIO_T: calculate_bi_quadratic,
    BDL_CurveFitTypes.BI_QUADRATIC_RATIO_DT: calculate_bi_quadratic,
}


def calculate_results_of_performance_curves(
    performance_curve_data: Dict[str, dict],
    evap_leaving_temp: float,
    condenser_entering_temp: float,
    load_ratio: float,
    load_ratio_is_plr: bool = False,
) -> dict:
    """
    Calculates and returns the results of performance curves for capacity (`cap_f_t`),
    efficiency (`eff_f_t`), energy input ratio (`eir_PLR`), and efficiency as a function
    of part-load ratio (`eff_f_plr`).

    The function evaluates various performance curves using temperature and load ratio inputs.
    It computes adjustments based on curve coefficients and ensures results adhere to minimum
    and maximum bounds.

    Parameters:
        performance_curve_data (Dict[str, Dict[str, Any]]):
            A dictionary containing performance curve coefficients, min/max outputs,
            and other related data.
        evap_leaving_temp (float): The evaporator leaving temperature.
        condenser_entering_temp (float): The condenser entering temperature.
        load_ratio (float): The current load ratio, typically between 0 and 1.
        load_ratio_is_plr (bool): Whether the load ratio is a part-load ratio (PLR).

    Returns:
        Dict[str, Any]: A dictionary containing:
            - `"cap_f_t"` (float): Capacity adjustment factor as a function of temperature.
            - `"eff_f_t"` (float): Efficiency adjustment factor as a function of temperature.
            - `"part_load_ratio"` (float): Computed part-load ratio.
            - `"eff_f_plr"` (float, optional): Efficiency adjustment factor as a function of PLR.
            - `"errors"` (List[str]): A list of error messages if any issues arise.
    """

    results = {
        "cap_f_t": None,
        "eff_f_t": None,
        "eff_f_plr": None,
        "errors": [],
    }

    coefficients = performance_curve_data["coefficients"]
    min_outputs = performance_curve_data["min_outputs"]
    max_outputs = performance_curve_data["max_outputs"]

    cap_f_t_curve_type = performance_curve_data["performance_curves"][
        "cap_f_t"
    ].get_inp(BDL_CurveFitKeywords.TYPE)
    eff_f_t_curve_type = performance_curve_data["performance_curves"][
        "eff_f_t"
    ].get_inp(BDL_CurveFitKeywords.TYPE)
    eff_f_plr_curve_type = performance_curve_data["performance_curves"][
        "eff_f_plr"
    ].get_inp(BDL_CurveFitKeywords.TYPE)

    # Capacity adjustment factor as a function of temperature can be Bi-Linear in T or Bi-Quadratic in T
    results["cap_f_t"] = CURVE_FUNCTION_MAP[cap_f_t_curve_type](
        coefficients["cap_f_t"],
        evap_leaving_temp,
        condenser_entering_temp,
        min_outputs["cap_f_t"],
        max_outputs["cap_f_t"],
    )

    # Efficiency adjustment factor as a function of temperature can be Bi-Linear in T or Bi-Quadratic in T
    results["eff_f_t"] = CURVE_FUNCTION_MAP[eff_f_t_curve_type](
        coefficients["eff_f_t"],
        evap_leaving_temp,
        condenser_entering_temp,
        min_outputs["eff_f_t"],
        max_outputs["eff_f_t"],
    )

    if load_ratio_is_plr:
        plr = load_ratio
    else:
        results["part_load_ratio"] = load_ratio / results["cap_f_t"]
        plr = results["part_load_ratio"]

    # Efficiency adjustment factor as a function of part load can be Quadratic, Cubic, or Bi-Quadratic in Ratio&DeltaT
    if eff_f_plr_curve_type in [BDL_CurveFitTypes.QUADRATIC, BDL_CurveFitTypes.CUBIC]:
        results["eff_f_plr"] = CURVE_FUNCTION_MAP[eff_f_plr_curve_type](
            coefficients["eff_f_plr"],
            plr,
            min_outputs["eff_f_plr"],
            max_outputs["eff_f_plr"],
        )
    elif eff_f_plr_curve_type == BDL_CurveFitTypes.BI_QUADRATIC_RATIO_DT:
        delta_temp = condenser_entering_temp - evap_leaving_temp
        results["eff_f_plr"] = calculate_bi_quadratic(
            coefficients["eff_f_plr"],
            plr,
            delta_temp,
            min_outputs["eff_f_plr"],
            max_outputs["eff_f_plr"],
        )
    else:
        results["errors"].append(
            f"Unsupported efficiency curve type: {eff_f_plr_curve_type}"
        )

    return results


def are_curve_outputs_all_equal_to_a_value_of_one(
    performance_curve_data: Dict[str, dict],
    evap_leaving_temp: float,
    condenser_entering_temp: float,
    decimal_margin_of_error: float,
) -> bool:
    """
    Checks whether the output of specific performance curves (`cap_f_t`, `eff_f_t`, and `eir_f_plr`)
    is approximately equal to 1 within a specified margin of error.

    This function assumes 100% load conditions and evaluates the performance curves used
    for capacity, efficiency, and energy input ratio (EIR) adjustments. The margin of error
    is expected to be given as a percentage (not a fraction), e.g., `1.5` for ±1.5%.

    Parameters:
        performance_curve_data (Dict[str, dict]): A dictionary containing performance curve data.
        evap_leaving_temp (float): The evaporator leaving temperature.
        condenser_entering_temp (float): The condenser entering temperature.
        decimal_margin_of_error (float): The allowable deviation from 1, expressed as a percentage.

    Returns:
        bool:
            - `True` if all curve outputs are within the specified margin of error.
            - `False` if any curve output deviates beyond the margin.
    """

    # Calculate and retrieve the results
    results = calculate_results_of_performance_curves(
        performance_curve_data,
        evap_leaving_temp,
        condenser_entering_temp,
        1.00,
    )

    is_cap_f_t_within_margin = is_within_margin(
        results["cap_f_t"], 1, decimal_margin_of_error
    )
    is_eff_f_t_within_margin = is_within_margin(
        results["eff_f_t"], 1, decimal_margin_of_error
    )
    is_eff_plr_within_margin = is_within_margin(
        results["eff_f_plr"], 1, decimal_margin_of_error
    )

    return all(
        [is_cap_f_t_within_margin, is_eff_f_t_within_margin, is_eff_plr_within_margin]
    )


def is_within_margin(value: float, target: float, decimal_margin: float) -> bool:
    """
    Determines whether a given value is within a specified percentage margin of a target value.

    Parameters:
        value (float): The value to check.
        target (float): The reference target value.
        decimal_margin (float): The allowable margin as a decimal (e.g., 0.05 for ±5%).

    Returns:
        bool: True if the value is within the margin, False otherwise.
    """
    lower_bound = target * (1 - decimal_margin)
    upper_bound = target * (1 + decimal_margin)
    return lower_bound <= value <= upper_bound


def adjust_capacity_for_user_defined_plr(
    plr_rated: float, capacity: float, cap_f_t_result: float
):
    """
    Adjusts the equipment capacity based on a user-defined part load ratio (PLR)
    and AHRI-rated conditions.

    This function modifies the given capacity to account for the user-defined PLR
    as specified in the eQuest UI and the capacity adjustment due to temperature
    variation.

    Parameters:
        plr_rated (float): The part load ratio defined in the eQuest UI.
        capacity (float): The unadjusted equipment capacity.
        cap_f_t_result (float): The capacity adjustment factor as a function of temperature.

    Returns:
        float: The adjusted equipment capacity.
    """

    capacity_adj = capacity * (1 / cap_f_t_result) * (1 / plr_rated)

    return capacity_adj
