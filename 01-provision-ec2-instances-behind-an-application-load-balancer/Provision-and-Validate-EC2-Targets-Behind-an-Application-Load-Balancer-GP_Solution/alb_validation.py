"""Deterministic validation for the ALB operational change record."""


def _mapping(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _meaningful(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() != "TODO"


def _normalise_text(value):
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().lower().split())


def _rule_matches(rule, expected):
    rule = _mapping(rule)
    return all(rule.get(key) == value for key, value in expected.items())


def validate_operational_record(record, deployment_brief, network_card, incident_card):
    """Validate a completed operational record without contacting AWS.

    The fixtures are treated as the authoritative deployment, network, and
    incident evidence. The returned structure is stable for assessment use.
    """
    record = _mapping(record)
    deployment_brief = _mapping(deployment_brief)
    network_card = _mapping(network_card)
    incident_card = _mapping(incident_card)
    errors = []

    deployment = _mapping(record.get("deployment"))
    instances = _list(deployment.get("instances"))
    listener = _mapping(deployment.get("listener"))
    target_group = _mapping(deployment.get("target_group"))

    intended_ids = deployment_brief.get("intended_instance_ids", [])
    intended_set = set(intended_ids)
    expected_count = deployment_brief.get("instance_count")
    expected_type = deployment_brief.get("instance_type")
    approved_subnets = {
        item.get("subnet_id")
        for item in _list(network_card.get("approved_subnets"))
        if isinstance(item, dict)
    }

    instance_ids = [item.get("instance_id") for item in instances if isinstance(item, dict)]
    identity_ok = (
        len(instances) == expected_count
        and len(instance_ids) == len(set(instance_ids))
        and set(instance_ids) == intended_set
        and all(item.get("instance_type") == expected_type for item in instances)
    )
    if not identity_ok:
        errors.append("DEPLOYMENT_IDENTITY_MISMATCH")

    instance_subnets = [item.get("subnet_id") for item in instances if isinstance(item, dict)]
    subnet_ok = (
        len(instance_subnets) == expected_count
        and all(subnet_id in approved_subnets for subnet_id in instance_subnets)
        and len(set(instance_subnets)) == expected_count
    )
    if not subnet_ok:
        errors.append("INSTANCE_SUBNET_NOT_APPROVED_OR_DISTINCT")

    expected_public = _mapping(deployment_brief.get("public_listener"))
    listener_ok = listener == {
        "load_balancer_id": deployment_brief.get("load_balancer_id"),
        "port": expected_public.get("port"),
        "protocol": expected_public.get("protocol"),
        "default_target_group_id": deployment_brief.get("target_group_id"),
    }
    if not listener_ok:
        errors.append("LISTENER_CONFIGURATION_MISMATCH")

    expected_application = _mapping(deployment_brief.get("application_listener"))
    expected_health = _mapping(deployment_brief.get("expected_health_endpoint"))
    target_identity_ok = (
        target_group.get("target_group_id") == deployment_brief.get("target_group_id")
        and target_group.get("protocol") == expected_application.get("protocol")
        and target_group.get("port") == expected_application.get("port")
        and target_group.get("healthy_status_codes") == [expected_health.get("status_code")]
    )
    if not target_identity_ok:
        errors.append("TARGET_GROUP_CONFIGURATION_MISMATCH")

    health_path_ok = target_group.get("health_check_path") == expected_health.get("path")
    if not health_path_ok:
        errors.append("HEALTH_CHECK_PATH_NOT_CORRECTED")

    validation = _mapping(record.get("validation"))
    target_health = _list(validation.get("target_health"))
    health_by_id = {
        item.get("instance_id"): item.get("state")
        for item in target_health
        if isinstance(item, dict)
    }
    all_targets_healthy = (
        len(target_health) == expected_count
        and set(health_by_id) == intended_set
        and all(health_by_id.get(instance_id) == "healthy" for instance_id in intended_ids)
    )
    if not all_targets_healthy:
        errors.append("INTENDED_TARGETS_NOT_ALL_HEALTHY")

    exactly_two_healthy = (
        identity_ok
        and subnet_ok
        and listener_ok
        and target_identity_ok
        and health_path_ok
        and all_targets_healthy
    )

    requests = _list(validation.get("requests"))
    expected_status = expected_health.get("status_code")
    successful_requests = [
        item
        for item in requests
        if isinstance(item, dict) and item.get("status_code") == expected_status
    ]
    minimum_requests = deployment_brief.get("minimum_successful_endpoint_requests", 0)
    enough_successes = len(successful_requests) >= minimum_requests
    if not enough_successes:
        errors.append("INSUFFICIENT_SUCCESSFUL_REQUESTS")

    observed_ids = {
        item.get("instance_id")
        for item in successful_requests
        if item.get("instance_id") in intended_set
    }
    both_ids_observed = observed_ids == intended_set
    if not both_ids_observed:
        errors.append("BOTH_INSTANCE_IDS_NOT_OBSERVED")

    security = _mapping(record.get("security"))
    alb_security_group = _mapping(security.get("load_balancer_security_group"))
    instance_security_group = _mapping(security.get("instance_security_group"))
    required_public_rule = _mapping(network_card.get("required_public_ingress"))
    required_instance_rule = _mapping(network_card.get("required_instance_ingress"))

    alb_rules = _list(alb_security_group.get("inbound_rules"))
    alb_ingress_ok = (
        alb_security_group.get("security_group_id")
        == network_card.get("load_balancer_security_group_id")
        and len(alb_rules) == 1
        and _rule_matches(alb_rules[0], required_public_rule)
    )
    if not alb_ingress_ok:
        errors.append("ALB_PUBLIC_INGRESS_MISMATCH")

    instance_rules = _list(instance_security_group.get("inbound_rules"))
    has_public_instance_rule = any(
        isinstance(rule, dict)
        and rule.get("source_cidr") in {"0.0.0.0/0", "::/0"}
        for rule in instance_rules
    )
    if has_public_instance_rule:
        errors.append("INSTANCE_INGRESS_PUBLIC")

    instance_ingress_ok = (
        instance_security_group.get("security_group_id")
        == network_card.get("instance_security_group_id")
        and len(instance_rules) == 1
        and _rule_matches(instance_rules[0], required_instance_rule)
        and not has_public_instance_rule
    )
    if not instance_ingress_ok and not has_public_instance_rule:
        errors.append("INSTANCE_INGRESS_NOT_ALB_ONLY")

    diagnosis = _mapping(record.get("diagnosis"))
    expected_cause = _normalise_text(incident_card.get("supported_diagnosis"))
    expected_correction = _normalise_text(incident_card.get("supported_correction"))
    cause_ok = _normalise_text(diagnosis.get("cause")) == expected_cause
    correction_ok = _normalise_text(diagnosis.get("correction")) == expected_correction
    if not cause_ok:
        errors.append("SEEDED_CAUSE_NOT_IDENTIFIED")
    if not correction_ok:
        errors.append("CORRECTION_NOT_SUPPORTED_BY_EVIDENCE")

    rollback = _mapping(record.get("rollback"))
    rollback_trigger_ok = _meaningful(rollback.get("trigger"))
    rollback_action_ok = _meaningful(rollback.get("action"))
    if not rollback_trigger_ok:
        errors.append("ROLLBACK_TRIGGER_MISSING")
    if not rollback_action_ok:
        errors.append("ROLLBACK_ACTION_MISSING")

    inventory = _list(record.get("inventory"))
    required_categories = set(deployment_brief.get("required_resource_categories", []))
    inventory_categories = {
        item.get("category") for item in inventory if isinstance(item, dict)
    }
    categories_ok = required_categories.issubset(inventory_categories)
    if not categories_ok:
        errors.append("REQUIRED_RESOURCE_CATEGORY_MISSING")

    inventoried_ids = set()
    inventory_ids_valid = True
    for item in inventory:
        if not isinstance(item, dict):
            inventory_ids_valid = False
            continue
        resource_ids = item.get("resource_ids")
        if not isinstance(resource_ids, list) or not resource_ids or not all(
            isinstance(resource_id, str) and resource_id for resource_id in resource_ids
        ):
            inventory_ids_valid = False
            continue
        inventoried_ids.update(resource_ids)
    categories_ok = categories_ok and inventory_ids_valid and bool(inventoried_ids)
    if not inventory_ids_valid and "REQUIRED_RESOURCE_CATEGORY_MISSING" not in errors:
        errors.append("REQUIRED_RESOURCE_CATEGORY_MISSING")

    cleanup = _mapping(record.get("cleanup"))
    removed_ids = set(_list(cleanup.get("removed_resource_ids")))
    all_removed = bool(inventoried_ids) and inventoried_ids.issubset(removed_ids)
    if not all_removed:
        errors.append("INVENTORIED_RESOURCE_NOT_REMOVED")

    zero_remaining = cleanup.get("remaining_chargeable_resource_count") == 0
    if not zero_remaining:
        errors.append("CHARGEABLE_RESOURCES_REMAIN")

    critical_checks = {
        "exactly_two_intended_targets_healthy": exactly_two_healthy,
        "at_least_six_successful_requests": enough_successes,
        "both_instance_ids_observed": both_ids_observed,
        "instance_ingress_only_from_alb_security_group": instance_ingress_ok and alb_ingress_ok,
    }
    diagnosis_checks = {
        "seeded_cause_identified": cause_ok,
        "correction_matches_evidence": correction_ok,
        "rollback_trigger_present": rollback_trigger_ok,
        "rollback_action_present": rollback_action_ok,
    }
    cleanup_checks = {
        "required_resource_categories_inventoried": categories_ok,
        "all_inventory_ids_removed": all_removed,
        "zero_chargeable_resources_remaining": zero_remaining,
    }

    critical_passed = all(critical_checks.values())
    diagnosis_passed = all(diagnosis_checks.values())
    cleanup_passed = all(cleanup_checks.values())
    components = {
        "critical_live_validation": {
            "passed": critical_passed,
            "checks": critical_checks,
        },
        "diagnosis_and_rollback": {
            "passed": diagnosis_passed,
            "checks": diagnosis_checks,
        },
        "inventory_and_cleanup": {
            "passed": cleanup_passed,
            "checks": cleanup_checks,
        },
    }

    return {
        "passed": all(component["passed"] for component in components.values()) and not errors,
        "errors": errors,
        "components": components,
        "critical_gates": [
            {
                "id": "GATE-1",
                "component": "critical_live_validation",
                "passed": critical_passed,
            }
        ],
    }