import copy
import json

import pytest

from validation.test_solution import (
    deployment_brief,
    incident_card,
    network_card,
    reference_record,
    validate,
)


def _instance_records(record):
    """Locate the existing instance evidence without duplicating its schema fixture."""
    matches = []

    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "instances" and isinstance(child, list):
                    if child and all(
                        isinstance(item, dict)
                        and "instance_id" in item
                        and "subnet_id" in item
                        for item in child
                    ):
                        matches.append(child)
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(record)
    assert len(matches) == 1, "The operational record must contain one instance evidence list"
    return matches[0]


def _assert_subnet_failure(report):
    assert report["passed"] is False
    assert "INSTANCE_SUBNET_NOT_APPROVED_OR_DISTINCT" in report["errors"]


def test_validator_rejects_two_targets_placed_in_the_same_approved_subnet(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    instances = _instance_records(record)

    assert [item["instance_id"] for item in instances] == ["i-0app0001", "i-0app0002"]
    assert [item["subnet_id"] for item in instances] == [
        "subnet-0aaa1111",
        "subnet-0bbb2222",
    ]

    instances[1]["subnet_id"] = instances[0]["subnet_id"]

    report = validate(record, deployment_brief, network_card, incident_card)

    _assert_subnet_failure(report)


def test_validator_rejects_a_target_in_a_nonapproved_subnet(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    instances = _instance_records(record)

    assert network_card["approved_subnets"] == [
        "subnet-0aaa1111",
        "subnet-0bbb2222",
    ]
    instances[1]["subnet_id"] = "subnet-0unapproved"

    report = validate(record, deployment_brief, network_card, incident_card)

    _assert_subnet_failure(report)


@pytest.mark.parametrize(
    "unsupported_cause",
    [
        "The target was unhealthy because its security group blocked TCP 8080 from sg-0alb001.",
        "The target was unhealthy because the application had not finished starting.",
        "The target was unhealthy because the target group used the wrong application port.",
    ],
)
def test_validator_rejects_plausible_but_unsupported_health_diagnoses(
    unsupported_cause,
    reference_record,
    deployment_brief,
    network_card,
    incident_card,
):
    record = copy.deepcopy(reference_record)

    assert incident_card["seeded_fault"]["observed_health_check_path"] == "/healthz"
    assert incident_card["seeded_fault"]["required_health_check_path"] == "/ready"
    record["diagnosis"]["cause"] = unsupported_cause

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["diagnosis_and_rollback"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert component["checks"]["seeded_cause_identified"] is False


def test_validator_rejects_one_unhealthy_intended_target(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    record["target_health"][1]["state"] = "unhealthy"

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["critical_live_validation"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert component["checks"]["exactly_two_intended_targets_healthy"] is False


def test_validator_rejects_fewer_than_six_successful_requests(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    assert len(record["endpoint_requests"]) == 6
    record["endpoint_requests"] = record["endpoint_requests"][:5]

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["critical_live_validation"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert component["checks"]["at_least_six_successful_requests"] is False


def test_validator_rejects_requests_that_observe_only_one_instance(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    for request in record["endpoint_requests"]:
        request["observed_instance_id"] = "i-0app0001"

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["critical_live_validation"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert component["checks"]["both_instance_ids_observed"] is False


def test_validator_rejects_public_instance_application_ingress(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    record["instance_security_group"]["inbound_rules"].append(
        {
            "protocol": "tcp",
            "from_port": 8080,
            "to_port": 8080,
            "source_cidr": "0.0.0.0/0",
        }
    )

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["critical_live_validation"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert (
        component["checks"]["instance_ingress_only_from_alb_security_group"]
        is False
    )


def test_validator_rejects_nonzero_remaining_chargeable_resources(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    record["cleanup"]["remaining_chargeable_resource_count"] = 1

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["inventory_and_cleanup"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert component["checks"]["zero_chargeable_resources_remaining"] is False


def test_validator_rejects_inventory_missing_a_required_resource_category(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    removed = record["inventory"].pop("target_groups")
    assert removed == ["tg-acme-app"]

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["inventory_and_cleanup"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert component["checks"]["required_resource_categories_inventoried"] is False


def test_validator_rejects_cleanup_missing_an_inventoried_resource_id(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    assert "sg-0app001" in record["cleanup"]["removed_resource_ids"]
    record["cleanup"]["removed_resource_ids"].remove("sg-0app001")

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["inventory_and_cleanup"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert component["checks"]["all_inventory_ids_removed"] is False


@pytest.mark.parametrize(
    ("field", "check_name"),
    [
        ("trigger", "rollback_trigger_present"),
        ("action", "rollback_action_present"),
    ],
)
def test_validator_requires_reproducible_rollback_trigger_and_action(
    field,
    check_name,
    reference_record,
    deployment_brief,
    network_card,
    incident_card,
):
    record = copy.deepcopy(reference_record)
    record["rollback"][field] = ""

    report = validate(record, deployment_brief, network_card, incident_card)

    component = report["components"]["diagnosis_and_rollback"]
    assert report["passed"] is False
    assert component["passed"] is False
    assert component["checks"][check_name] is False