from jev_router_demo.scenarios import SCENARIOS


def test_catalog_contains_long_distinct_requests_and_both_sides_of_routing_choices():
    assert len(SCENARIOS) == 16
    assert all(2000 <= len(item.request) <= 5000 for item in SCENARIOS)
    assert len({item.request for item in SCENARIOS}) == 16
    assert all(item.summary and item.expected_tiers for item in SCENARIOS)
    assert {item.category for item in SCENARIOS} == {"work", "coding", "research", "analysis", "operations"}
    assert {item.expected_web for item in SCENARIOS} == {False, True}
    assert {item.expected_approval for item in SCENARIOS} == {False, True}


def test_recommended_and_category_search_keep_original_catalog_ids():
    from jev_router_demo.scenarios import scenario_indices

    recommended = scenario_indices()
    assert len(recommended) == 6
    assert all(SCENARIOS[index].recommended for index in recommended)
    assert scenario_indices("all") == list(range(16))
    assert scenario_indices("operations") == [4, 15]
    assert scenario_indices("all", "  고객  ") == [7]
    assert scenario_indices("work", "고객") == [7]
    assert scenario_indices("coding", "고객") == []
    assert scenario_indices("all", "nonexistent scenario") == []


def test_metadata_pairs_distinguish_existing_facts_and_analysis_from_live_lookup_and_execution():
    supplied = SCENARIOS[12]
    live = SCENARIOS[10]
    audit = SCENARIOS[14]
    deletion = SCENARIOS[4]
    assert supplied.expected_web is False and live.expected_web is True
    assert audit.expected_approval is False and deletion.expected_approval is True
