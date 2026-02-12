from uuid import uuid4

from hope.apps.dashboard.services import DashboardDataCache, DashboardGlobalDataCache


def test_create_empty_country_summary_returns_correct_keys():
    result = DashboardDataCache._create_empty_country_summary()
    expected_keys = {
        "total_usd",
        "total_quantity",
        "total_payments",
        "individuals",
        "children_counts",
        "pwd_counts",
        "reconciled_count",
        "finished_payment_plans",
        "total_payment_plans",
        "planned_sum_for_group",
        "_seen_households",
    }
    assert set(result.keys()) == expected_keys


def test_create_empty_country_summary_default_values():
    result = DashboardDataCache._create_empty_country_summary()
    assert result["total_usd"] == 0.0
    assert result["total_quantity"] == 0.0
    assert result["total_payments"] == 0
    assert result["individuals"] == 0
    assert result["children_counts"] == 0.0
    assert result["pwd_counts"] == 0
    assert result["reconciled_count"] == 0
    assert result["finished_payment_plans"] == 0
    assert result["total_payment_plans"] == 0
    assert result["planned_sum_for_group"] == 0.0
    assert result["_seen_households"] == set()


def test_create_empty_country_summary_returns_new_set_each_call():
    result1 = DashboardDataCache._create_empty_country_summary()
    result2 = DashboardDataCache._create_empty_country_summary()
    result1["_seen_households"].add(uuid4())
    assert len(result2["_seen_households"]) == 0


def test_build_country_summary_results_empty_summary():
    result = DashboardDataCache._build_country_summary_results({})
    assert result == []


def test_build_country_summary_results_single_entry():
    hh_id = uuid4()
    summary = {
        (2024, 3, "Admin1Area", "ProgramX", "Education", "FSP1", "Cash", "Distributed", "USD"): {
            "total_usd": 1500.50,
            "total_quantity": 100.0,
            "total_payments": 10,
            "individuals": 25,
            "children_counts": 7.6,
            "pwd_counts": 3,
            "reconciled_count": 5,
            "finished_payment_plans": 2,
            "total_payment_plans": 4,
            "planned_sum_for_group": 2000.0,
            "_seen_households": {hh_id},
        }
    }
    results = DashboardDataCache._build_country_summary_results(summary)
    assert len(results) == 1
    r = results[0]
    assert r["year"] == 2024
    assert r["month"] == "March"
    assert r["admin1"] == "Admin1Area"
    assert r["program"] == "ProgramX"
    assert r["sector"] == "Education"
    assert r["fsp"] == "FSP1"
    assert r["delivery_types"] == "Cash"
    assert r["status"] == "Distributed"
    assert r["currency"] == "USD"
    assert r["total_delivered_quantity_usd"] == 1500.50
    assert r["total_delivered_quantity"] == 100.0
    assert r["payments"] == 10
    assert r["households"] == 1
    assert r["individuals"] == 25
    assert r["children_counts"] == 8  # int(round(7.6))
    assert r["pwd_counts"] == 3
    assert r["reconciled"] == 5
    assert r["finished_payment_plans"] == 2
    assert r["total_payment_plans"] == 4
    assert r["total_planned_usd"] == 2000.0


def test_build_country_summary_results_month_name_mapping():
    base_totals = DashboardDataCache._create_empty_country_summary()
    base_totals["total_payments"] = 1

    summary = {}
    for month_num in range(1, 13):
        key = (2024, month_num, "A", "P", "S", "F", "D", "St", "C")
        summary[key] = {**base_totals, "_seen_households": set()}

    results = DashboardDataCache._build_country_summary_results(summary)
    month_names = {r["month"] for r in results}
    expected_months = {
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    }
    assert month_names == expected_months


def test_build_country_summary_results_invalid_month_gives_unknown():
    base_totals = DashboardDataCache._create_empty_country_summary()
    summary = {
        (2024, None, "A", "P", "S", "F", "D", "St", "C"): base_totals,
    }
    results = DashboardDataCache._build_country_summary_results(summary)
    assert results[0]["month"] == "Unknown"


def test_build_country_summary_results_month_zero_gives_unknown():
    base_totals = DashboardDataCache._create_empty_country_summary()
    summary = {
        (2024, 0, "A", "P", "S", "F", "D", "St", "C"): base_totals,
    }
    results = DashboardDataCache._build_country_summary_results(summary)
    assert results[0]["month"] == "Unknown"


def test_build_country_summary_results_month_13_gives_unknown():
    base_totals = DashboardDataCache._create_empty_country_summary()
    summary = {
        (2024, 13, "A", "P", "S", "F", "D", "St", "C"): base_totals,
    }
    results = DashboardDataCache._build_country_summary_results(summary)
    assert results[0]["month"] == "Unknown"


def test_build_country_summary_results_children_counts_rounded():
    base_totals = DashboardDataCache._create_empty_country_summary()
    base_totals["children_counts"] = 3.5
    summary = {
        (2024, 1, "A", "P", "S", "F", "D", "St", "C"): base_totals,
    }
    results = DashboardDataCache._build_country_summary_results(summary)
    assert results[0]["children_counts"] == 4


def test_build_country_summary_results_multiple_entries():
    totals1 = DashboardDataCache._create_empty_country_summary()
    totals1["total_usd"] = 100.0
    totals1["total_payments"] = 5
    totals2 = DashboardDataCache._create_empty_country_summary()
    totals2["total_usd"] = 200.0
    totals2["total_payments"] = 10
    summary = {
        (2024, 1, "A1", "P1", "S1", "F1", "D1", "St1", "C1"): totals1,
        (2024, 2, "A2", "P2", "S2", "F2", "D2", "St2", "C2"): totals2,
    }
    results = DashboardDataCache._build_country_summary_results(summary)
    assert len(results) == 2
    usd_values = {r["total_delivered_quantity_usd"] for r in results}
    assert usd_values == {100.0, 200.0}


# --- DashboardGlobalDataCache tests ---


def test_global_create_empty_summary_returns_correct_keys():
    result = DashboardGlobalDataCache._create_empty_summary()
    expected_keys = {
        "total_usd",
        "total_payments",
        "individuals",
        "children_counts",
        "pwd_counts",
        "reconciled_count",
        "finished_payment_plans",
        "total_payment_plans",
        "planned_sum_for_group",
        "_seen_households",
    }
    assert set(result.keys()) == expected_keys


def test_global_create_empty_summary_default_values():
    result = DashboardGlobalDataCache._create_empty_summary()
    assert result["total_usd"] == 0.0
    assert result["total_payments"] == 0
    assert result["individuals"] == 0
    assert result["children_counts"] == 0.0
    assert result["pwd_counts"] == 0
    assert result["reconciled_count"] == 0
    assert result["finished_payment_plans"] == 0
    assert result["total_payment_plans"] == 0
    assert result["planned_sum_for_group"] == 0.0
    assert result["_seen_households"] == set()


def test_global_create_empty_summary_no_total_quantity_key():
    result = DashboardGlobalDataCache._create_empty_summary()
    assert "total_quantity" not in result


def test_global_create_empty_summary_returns_new_set_each_call():
    result1 = DashboardGlobalDataCache._create_empty_summary()
    result2 = DashboardGlobalDataCache._create_empty_summary()
    result1["_seen_households"].add(uuid4())
    assert len(result2["_seen_households"]) == 0


def test_global_build_summary_results_empty():
    result = DashboardGlobalDataCache._build_summary_results({})
    assert result == []


def test_global_build_summary_results_single_entry():
    hh_ids = {uuid4(), uuid4()}
    summary = {
        (2024, "Afghanistan", "South Asia", "Education", "Cash", "Distributed"): {
            "total_usd": 5000.0,
            "total_payments": 20,
            "individuals": 50,
            "children_counts": 12.3,
            "pwd_counts": 5,
            "reconciled_count": 10,
            "finished_payment_plans": 3,
            "total_payment_plans": 6,
            "planned_sum_for_group": 8000.0,
            "_seen_households": hh_ids,
        }
    }
    results = DashboardGlobalDataCache._build_summary_results(summary)
    assert len(results) == 1
    r = results[0]
    assert r["year"] == 2024
    assert r["country"] == "Afghanistan"
    assert r["region"] == "South Asia"
    assert r["sector"] == "Education"
    assert r["delivery_types"] == "Cash"
    assert r["status"] == "Distributed"
    assert r["total_delivered_quantity_usd"] == 5000.0
    assert r["payments"] == 20
    assert r["households"] == 2
    assert r["individuals"] == 50
    assert r["children_counts"] == 12  # int(round(12.3))
    assert r["pwd_counts"] == 5
    assert r["reconciled"] == 10
    assert r["finished_payment_plans"] == 3
    assert r["total_payment_plans"] == 6
    assert r["total_planned_usd"] == 8000.0


def test_global_build_summary_results_children_counts_rounded():
    base = DashboardGlobalDataCache._create_empty_summary()
    base["children_counts"] = 2.5
    summary = {
        (2024, "Country", "Region", "Sector", "DT", "Status"): base,
    }
    results = DashboardGlobalDataCache._build_summary_results(summary)
    assert results[0]["children_counts"] == 2  # int(round(2.5)) = 2 (banker's rounding)


def test_global_build_summary_results_multiple_entries():
    totals1 = DashboardGlobalDataCache._create_empty_summary()
    totals1["total_usd"] = 1000.0
    totals1["total_payments"] = 5
    totals2 = DashboardGlobalDataCache._create_empty_summary()
    totals2["total_usd"] = 2000.0
    totals2["total_payments"] = 10
    summary = {
        (2024, "Country1", "Region1", "Sector1", "DT1", "Status1"): totals1,
        (2025, "Country2", "Region2", "Sector2", "DT2", "Status2"): totals2,
    }
    results = DashboardGlobalDataCache._build_summary_results(summary)
    assert len(results) == 2
    years = {r["year"] for r in results}
    assert years == {2024, 2025}


def test_global_build_summary_results_no_month_field():
    """Global summary results should not have a 'month' field."""
    base = DashboardGlobalDataCache._create_empty_summary()
    summary = {
        (2024, "Country", "Region", "Sector", "DT", "Status"): base,
    }
    results = DashboardGlobalDataCache._build_summary_results(summary)
    assert "month" not in results[0]


def test_global_build_summary_results_no_total_delivered_quantity_field():
    """Global summary results should not have 'total_delivered_quantity' (non-USD)."""
    base = DashboardGlobalDataCache._create_empty_summary()
    summary = {
        (2024, "Country", "Region", "Sector", "DT", "Status"): base,
    }
    results = DashboardGlobalDataCache._build_summary_results(summary)
    assert "total_delivered_quantity" not in results[0]
