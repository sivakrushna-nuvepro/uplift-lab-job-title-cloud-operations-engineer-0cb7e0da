import copy
import json
from pathlib import Path

import pytest

from reference_project.alb_validation import validate_operational_record


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
PROJECT = ROOT / "reference_project"


def read_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture
def deployment_brief():
    return read_json(FIXTURES / "deployment_brief.json")


@pytest.fixture
def network_card():
    return read_json(FIXTURES / "network_card.json")


@pytest.fixture
def incident_card():
    return read_json(FIXTURES / "health_incident_card.json")


@pytest.fixture
def reference_record():
    return read_json(
        PROJECT / "reference-solution" / "operational-change-record.json"
    )


def validate(record, deployment_brief, network_card, incident_card):
    return validate_operational_record(
        record=record,
        deployment_brief=deployment_brief,
        network_card=network_card,
        incident_card=incident_card,
    )


def test_repository_contains_one_paired_simulation_and_practical_assessment():
    manifest = read_json(PROJECT / "lab_manifest.json")

    assert manifest["title"] == "Provision EC2 instances behind an Application Load Balancer"
    assert manifest["difficulty"] == "Proficient"
    assert manifest["pairing_mode"] == "paired"
    assert manifest["total_hours"] == 3.0
    assert manifest["counts"] == {
        "simulations": 1,
        "practical_assessments": 1,
        "mcq_assessments": 0,
    }
    assert len(manifest["exercises"]) == 2
    assert manifest["exercises"][0] == {
        "kind": "simulation",
        "index": 1,
        "hours": 1.5,
        "title": "Restore and Prove a Secure Load-Balanced Application",
    }
    assert manifest["exercises"][1] == {
        "kind": "practical-assessment",
        "index": 1,
        "paired_simulation_index": 1,
        "hours": 1.5,
        "title": "Provision and Validate EC2 Targets Behind an Application Load Balancer",
    }
    assert manifest["requirement_ids"] == ["REQ-001", "REQ-002"]
    assert manifest["source_paths"] == [
        "prior-samples/selection.md",
        "prior-samples/source-excerpt.md",
    ]


def test_guided_instructions_cover_build_diagnosis_evidence_and_ordered_cleanup():
    text = (PROJECT / "guided-instructions" / "simulation.md").read_text(
        encoding="utf-8"
    )

    required_sections = [
        "## Scenario",
        "## Deployment brief",
        "## Guided steps",
        "## Diagnose before changing",
        "## Capture evidence before teardown",
        "## Rollback",
        "## Cleanup and final cost check",
        "## Copilot-assisted handoff",
    ]
    for section in required_sections:
        assert section in text

    assert "i-0acmeapp01" in text
    assert "i-0acmeapp02" in text
    assert "subnet-0aaa1111" in text
    assert "subnet-0bbb2222" in text
    assert "six successful" in text.lower()
    assert "sanitize" in text.lower()
    assert "verify every copilot statement" in text.lower()

    capture_position = text.index("## Capture evidence before teardown")
    cleanup_position = text.index("## Cleanup and final cost check")
    assert capture_position < cleanup_position


def test_practice_workspace_is_distinct_and_has_uncompleted_evidence_fields():
    template_path = (
        PROJECT
        / "practice-solution"
        / "operational-change-record.template.json"
    )
    reference_path = (
        PROJECT / "reference-solution" / "operational-change-record.json"
    )
    template = read_json(template_path)
    reference = read_json(reference_path)

    assert template_path != reference_path
    assert template != reference
    assert template["record_status"] == "learner-draft"
    assert template["validation"]["target_health"] == []
    assert template["validation"]["requests"] == []
    assert template["diagnosis"]["cause"] == "TODO"
    assert template["diagnosis"]["correction"] == "TODO"
    assert template["rollback"]["trigger"] == "TODO"
    assert template["rollback"]["action"] == "TODO"
    assert template["cleanup"]["remaining_chargeable_resource_count"] is None


def test_reference_record_passes_all_three_assessment_components(
    reference_record, deployment_brief, network_card, incident_card
):
    report = validate(
        reference_record, deployment_brief, network_card, incident_card
    )

    assert report["passed"] is True
    assert report["errors"] == []
    assert report["components"] == {
        "critical_live_validation": {
            "passed": True,
            "checks": {
                "exactly_two_intended_targets_healthy": True,
                "at_least_six_successful_requests": True,
                "both_instance_ids_observed": True,
                "instance_ingress_only_from_alb_security_group": True,
            },
        },
        "diagnosis_and_rollback": {
            "passed": True,
            "checks": {
                "seeded_cause_identified": True,
                "correction_matches_evidence": True,
                "rollback_trigger_present": True,
                "rollback_action_present": True,
            },
        },
        "inventory_and_cleanup": {
            "passed": True,
            "checks": {
                "required_resource_categories_inventoried": True,
                "all_inventory_ids_removed": True,
                "zero_chargeable_resources_remaining": True,
            },
        },
    }
    assert report["critical_gates"] == [
        {
            "id": "GATE-1",
            "component": "critical_live_validation",
            "passed": True,
        }
    ]


def test_reference_record_proves_exact_targets_listener_health_and_subnets(
    reference_record, deployment_brief, network_card, incident_card
):
    report = validate(
        reference_record, deployment_brief, network_card, incident_card
    )
    deployment = reference_record["deployment"]

    assert deployment["instances"] == [
        {
            "instance_id": "i-0acmeapp01",
            "instance_type": "t3.micro",
            "subnet_id": "subnet-0aaa1111",
        },
        {
            "instance_id": "i-0acmeapp02",
            "instance_type": "t3.micro",
            "subnet_id": "subnet-0bbb2222",
        },
    ]
    assert deployment["listener"] == {
        "load_balancer_id": "alb-acme-ops",
        "port": 443,
        "protocol": "HTTPS",
        "default_target_group_id": "tg-acme-app",
    }
    assert deployment["target_group"] == {
        "target_group_id": "tg-acme-app",
        "protocol": "HTTP",
        "port": 8080,
        "health_check_path": "/ready",
        "healthy_status_codes": [200],
    }
    assert report["passed"] is True


def test_reference_record_has_six_successes_and_routes_to_both_instances(
    reference_record, deployment_brief, network_card, incident_card
):
    report = validate(
        reference_record, deployment_brief, network_card, incident_card
    )
    requests = reference_record["validation"]["requests"]

    assert len(requests) == 6
    assert [item["status_code"] for item in requests] == [200] * 6
    assert {item["instance_id"] for item in requests} == {
        "i-0acmeapp01",
        "i-0acmeapp02",
    }
    assert report["components"]["critical_live_validation"]["passed"] is True


def test_public_instance_ingress_from_fixture_is_rejected(
    reference_record, deployment_brief, network_card, incident_card
):
    insecure_rule = read_json(FIXTURES / "insecure_instance_ingress.json")
    record = copy.deepcopy(reference_record)
    record["security"]["instance_security_group"]["inbound_rules"] = [
        insecure_rule
    ]

    report = validate(record, deployment_brief, network_card, incident_card)

    assert report["passed"] is False
    assert report["components"]["critical_live_validation"]["passed"] is False
    assert report["components"]["critical_live_validation"]["checks"][
        "instance_ingress_only_from_alb_security_group"
    ] is False
    assert "INSTANCE_INGRESS_PUBLIC" in report["errors"]


def test_wrong_health_path_and_one_healthy_target_fail_the_critical_gate(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    record["deployment"]["target_group"]["health_check_path"] = "/healthz"
    record["validation"]["target_health"][1]["state"] = "unhealthy"

    report = validate(record, deployment_brief, network_card, incident_card)

    assert report["passed"] is False
    assert report["critical_gates"] == [
        {
            "id": "GATE-1",
            "component": "critical_live_validation",
            "passed": False,
        }
    ]
    assert "HEALTH_CHECK_PATH_NOT_CORRECTED" in report["errors"]
    assert "INTENDED_TARGETS_NOT_ALL_HEALTHY" in report["errors"]


def test_cleanup_must_remove_every_inventoried_resource_and_report_zero(
    reference_record, deployment_brief, network_card, incident_card
):
    record = copy.deepcopy(reference_record)
    record["cleanup"]["removed_resource_ids"].remove("alb-acme-ops")
    record["cleanup"]["remaining_chargeable_resource_count"] = 1

    report = validate(record, deployment_brief, network_card, incident_card)

    assert report["passed"] is False
    assert report["components"]["inventory_and_cleanup"] == {
        "passed": False,
        "checks": {
            "required_resource_categories_inventoried": True,
            "all_inventory_ids_removed": False,
            "zero_chargeable_resources_remaining": False,
        },
    }
    assert "INVENTORIED_RESOURCE_NOT_REMOVED" in report["errors"]
    assert "CHARGEABLE_RESOURCES_REMAIN" in report["errors"]


def test_assessment_answer_key_has_one_item_per_component_and_marks_gate():
    assessment = (PROJECT / "assessment" / "practical-assessment.md").read_text(
        encoding="utf-8"
    )
    answer_key = read_json(PROJECT / "assessment" / "answer-key.json")

    assert "capture" in assessment.lower()
    assert "before teardown" in assessment.lower()
    assert "at least six" in assessment.lower()
    assert len(answer_key["items"]) == 3
    assert [item["component"] for item in answer_key["items"]] == [
        "critical_live_validation",
        "diagnosis_and_rollback",
        "inventory_and_cleanup",
    ]
    assert answer_key["items"][0]["critical_gate"] is True
    assert answer_key["items"][0]["gate_id"] == "GATE-1"
    assert answer_key["items"][1]["critical_gate"] is False
    assert answer_key["items"][2]["critical_gate"] is False
    assert sum(item["critical_gate"] for item in answer_key["items"]) == 1