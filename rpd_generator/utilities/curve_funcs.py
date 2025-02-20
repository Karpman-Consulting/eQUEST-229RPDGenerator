from rpd_generator.bdl_structure.bdl_enumerations.bdl_enums import BDLEnums


BDL_CurveFitKeywords = BDLEnums.bdl_enums["CurveFitKeywords"]
BDL_CurveFitInputTypes = BDLEnums.bdl_enums["CurveFitInputTypes"]
BDL_CurveFitTypes = BDLEnums.bdl_enums["CurveFitTypes"]


def calculate_bi_quadratic(
    curve_coeffs: list, x: float, y: float, min_val: float, max_val: float
) -> float:
    """Function takes a list of curve coefficients with a = 0 index and f = 5th index and two independent variables x and y.
    Function then computes and returns Z = a + b * x + c * x^2 + d * y + e * y^2 + f * x * y ensuring z is within the range min_val and max_val
    This function works for any eQuest BI-QUADRATIC curve
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
    curve_coeffs: list, x: float, min_val: float, max_val: float
) -> float:
    """Function takes a list of curve coefficients with a = 0 index and d = 3rd index and an independent variable X.
    Function then computes and returns Z = a + b * X + c * X^2 + d * X^3 ensuring z is within the range min_val and max_val
    """
    z = (
        curve_coeffs[0]
        + curve_coeffs[1] * x
        + curve_coeffs[2] * x**2
        + curve_coeffs[3] * x**3
    )

    # Ensure z is within the range [min_val, max_val]
    z = max(min_val, min(z, max_val))

    return z


def calculate_quadratic(
    curve_coeffs: list, x: float, min_val: float, max_val: float
) -> float:
    """Function takes a list of curve coefficients with a = 0 index and c = 2nd index and an independent variable X.
    Function then computes and returns Z = a + b * X + c * X^2 ensuring z is within the range min_val and max_val
    """
    z = curve_coeffs[0] + curve_coeffs[1] * x + curve_coeffs[2] * x**2

    # Ensure z is within the range [min_val, max_val]
    z = max(min_val, min(z, max_val))

    return z


CURVE_FUNCTION_MAP = {
    BDL_CurveFitTypes.QUADRATIC: calculate_quadratic,
    BDL_CurveFitTypes.CUBIC: calculate_cubic,
}


def calculate_results_of_performance_curves(
    performance_curve_data,
    evap_leaving_temp,
    condenser_entering_temp,
    eff_f_plr_curve_type,
    load_ratio,
):
    """Returns the results of performance curves and partload ratio for cap_f_t, eir_PLR, eir_f_t"""

    coefficients = performance_curve_data["coefficients"]
    min_outputs = performance_curve_data["min_outputs"]
    max_outputs = performance_curve_data["max_outputs"]

    cap_f_t_result = calculate_bi_quadratic(
        coefficients["cap_f_t_coeffs"],
        evap_leaving_temp,
        condenser_entering_temp,
        min_outputs["cap_f_t_min_output"],
        max_outputs["cap_f_t_max_output"],
    )
    eff_f_t_result = calculate_bi_quadratic(
        coefficients["eff_f_t_coeffs"],
        evap_leaving_temp,
        condenser_entering_temp,
        min_outputs["eff_f_t_min_output"],
        max_outputs["eff_f_t_max_output"],
    )
    adj_part_load_ratio = load_ratio / cap_f_t_result

    if eff_f_plr_curve_type in CURVE_FUNCTION_MAP:
        eff_f_plr_result = CURVE_FUNCTION_MAP[eff_f_plr_curve_type](
            coefficients["eff_f_plr_coeffs"],
            adj_part_load_ratio,
            min_outputs["eff_f_plr_min_output"],
            max_outputs["eff_f_plr_max_output"],
        )
    else:
        delta_temp = condenser_entering_temp - evap_leaving_temp
        eff_f_plr_result = calculate_bi_quadratic(
            coefficients["eff_f_plr_coeffs"],
            adj_part_load_ratio,
            delta_temp,
            min_outputs["eff_f_plr_min_output"],
            max_outputs["eff_f_plr_max_output"],
        )
    results = {
        "cap_f_t_result": cap_f_t_result,
        "eff_f_t_result": eff_f_t_result,
        "part_load_ratio": adj_part_load_ratio,
        "eff_f_plr_result": eff_f_plr_result,
    }
    return results


def are_curve_outputs_all_equal_to_a_value_of_one(
    performance_curve_data: dict,
    evap_leaving_temp: float,
    condenser_entering_temp: float,
    percent_margin_of_error: float,
) -> [bool, None]:
    """This assumes 100% load. The function checks whether the output of each curve is equal to 1 with the specified margin of error.
    The function returns a True or False. This was created to assess cap_f_t, eff_ct, and eir_f_plr curves only. The margin of error
    is expected to be a number from 0 to 100 (not a fraction). Default based on observations of curves 1.5.
    """

    eff_f_plr_curve_type = performance_curve_data["performance_curves"][
        "cap_f_t"
    ].get_inp(BDL_CurveFitKeywords.TYPE)

    # Calculate and retrieve the results
    results = calculate_results_of_performance_curves(
        performance_curve_data,
        evap_leaving_temp,
        condenser_entering_temp,
        eff_f_plr_curve_type,
        1.00,
    )

    is_cap_f_t_within_margin = is_within_margin(
        results["cap_f_t_result"], 1, percent_margin_of_error
    )
    is_eff_f_t_within_margin = is_within_margin(
        results["eff_f_t_result"], 1, percent_margin_of_error
    )
    is_eff_plr_within_margin = is_within_margin(
        results["eff_f_plr_result"], 1, percent_margin_of_error
    )

    return all(
        [is_cap_f_t_within_margin, is_eff_f_t_within_margin, is_eff_plr_within_margin]
    )


def is_within_margin(value, target, percent_margin):
    lower_bound = target * (1 - percent_margin)
    upper_bound = target * (1 + percent_margin)
    return lower_bound <= value <= upper_bound


def adjust_capacity_for_user_defined_plr(
    plr_rated: float, capacity: float, capft_result: float
):
    """Function adjusts capacity for the situation when part load ratio rated in defined.
    This formula adjusts to AHRI rated conditions. plr_rated is the part load ratio defined in the
    eQuest UI. Capacity is the unadjusted capacity. cap_f_t_result is the results of the capacity as
    a function of temperature curve"""

    capacity_adj = capacity * (1 / capft_result) * (1 / plr_rated)

    return capacity_adj


def get_output_of_curves_at_temperature_and_load_conditions(
    performance_curve_data,
    evap_leaving_temp: float,
    cond_entering_temp: float,
    load: float,
):
    """Returns the results of the Cap_f_t curve given the temperatures and % load sent to the function."""

    cap_f_t = performance_curve_data["performance_curves"]["cap_f_t"]
    cap_f_t_curve_type = cap_f_t.get_inp(BDL_CurveFitKeywords.TYPE)

    results = calculate_results_of_performance_curves(
        performance_curve_data,
        evap_leaving_temp,
        cond_entering_temp,
        cap_f_t_curve_type,
        load,
    )

    return results


def calculate_eff_performance_curve_results(
    evap_leaving_temp: int,
    condenser_entering_temp: int,
    performance_curve_data: dict,
    part_load_ratio: float,
) -> dict:
    """
    Calculate efficiency performance curve results based on temperature conditions,
    curve coefficients, and part-load ratio.

    This function evaluates efficiency performance curves using given evaporator
    and condenser temperatures, along with the part-load ratio, to determine
    efficiency adjustment factors.

    Parameters:
        evap_leaving_temp (int):
            The evaporator leaving temperature in degrees Fahrenheit.
        condenser_entering_temp (int):
            The condenser entering temperature in degrees Fahrenheit.
        performance_curve_data (dict):
            A dictionary containing curve objects, including coefficients
            and output range values.
        part_load_ratio (float):
            The part-load ratio at which efficiency is evaluated.

    Returns:
        dict: A dictionary containing:
            - `"eff_f_t_result"` (float or None): The efficiency adjustment factor as
              a function of temperature.
            - `"eff_f_plr_result"` (float or None): The efficiency adjustment factor
              as a function of part-load ratio.
            - `"errors"` (list): A list of error messages, if any.

    Notes:
        - The function determines the appropriate curve function type (quadratic,
          cubic, or bi-quadratic) and applies it to compute efficiency results.
        - If the efficiency adjustment curve type is unsupported, a bi-quadratic
          calculation is performed using the part-load ratio and chilled water delta-T.
    """

    results = {
        "eff_f_t_result": None,
        "eff_f_plr_result": None,
        "errors": [],
    }

    eff_f_plr_curve_type = performance_curve_data["performance_curves"][
        "cap_f_t"
    ].get_inp(BDL_CurveFitKeywords.TYPE)

    results["eff_f_t_result"] = calculate_bi_quadratic(
        performance_curve_data["coefficients"]["eff_f_t_coeffs"],
        evap_leaving_temp,
        condenser_entering_temp,
        performance_curve_data["min_outputs"]["eff_f_t_min_output"],
        performance_curve_data["max_outputs"]["eff_f_t_max_output"],
    )

    if eff_f_plr_curve_type in CURVE_FUNCTION_MAP:
        results["eff_f_plr_result"] = CURVE_FUNCTION_MAP[eff_f_plr_curve_type](
            performance_curve_data["coefficients"]["eff_f_plr_coeffs"],
            part_load_ratio,
            performance_curve_data["min_outputs"]["eff_f_plr_min_output"],
            performance_curve_data["max_outputs"]["eff_f_plr_max_output"],
        )
    else:
        chw_delta_t = condenser_entering_temp - evap_leaving_temp
        results["eff_f_plr_result"] = calculate_bi_quadratic(
            performance_curve_data["coefficients"]["eff_f_plr_coeffs"],
            part_load_ratio,
            chw_delta_t,
            performance_curve_data["min_outputs"]["eff_f_plr_min_output"],
            performance_curve_data["max_outputs"]["eff_f_plr_max_output"],
        )

    return results
