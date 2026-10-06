# Provision and Validate EC2 Targets Behind an Application Load Balancer

**Kind:** Practical assessment paired with Simulation 1  
**Duration:** 1.5 hours  
**Difficulty:** Proficient

## Assessment scenario

In a fresh scoped AWS sandbox, independently establish the specified two-instance application behind an Application Load Balancer. One target-health failure is seeded. Use the supplied deployment brief, network card, incident evidence, and live AWS observations to distinguish the actual fault from plausible path, port, response-code, startup, and network-rule explanations.

Submit one completed copy of `reference_project/practice-solution/operational-change-record.template.json`. Microsoft 365 Copilot may structure sanitized evidence, but every submitted statement must be reconciled with an observed result.

## Required sequence

1. Provision exactly the two intended `t3.micro` EC2 application instances from the approved image across the two approved subnets.
2. Configure the ALB HTTPS/443 listener to forward to the intended HTTP/8080 target group.
3. Permit public inbound traffic only on the required ALB service port. Permit instance TCP/8080 ingress from the ALB security group, never from a public CIDR.
4. Observe the initial target-health failure and supporting application/network evidence. Identify the seeded cause before changing configuration, apply only the evidence-supported correction, and wait for both intended targets to become healthy.
5. While resources remain live, capture target-health, listener, target-group, and ingress observations. Make at least six successful requests through the ALB and record status 200 plus the responding instance ID for each request. The observations must include both intended instance IDs.
6. Capture the complete learner-created resource inventory and all critical live evidence before teardown.
7. Document a reproducible rollback trigger and action.
8. Tear down all learner-created chargeable resources in dependency-aware order, then perform and record a distinct final zero-resource check.
9. Sanitize evidence supplied to Copilot, review its draft, and correct every claim not supported by the recorded AWS observations.

## Assessed components

### 1. Critical live validation — GATE-1

Pass requires all of the following evidence captured before teardown:

- Exactly the two intended targets are healthy.
- At least six ALB endpoint requests succeeded with status 200.
- The request observations collectively identify both intended instance IDs.
- Instance application-port ingress is sourced only from the ALB security group and is not public.

Failure of this component fails the assessment even if the other components pass.

### 2. Diagnosis and rollback

The record must identify the seeded health-check cause from the supplied and observed evidence, describe the matching minimal correction, and reject unsupported network or application explanations. It must state a reproducible rollback trigger and a concrete rollback action that preserves the security boundary.

### 3. Inventory and cleanup

The inventory must include the learner-created EC2, load-balancer, target-group, and security-group resources. Every inventoried resource ID must appear in removal evidence. A final check performed after teardown must report zero learner-created chargeable resources remaining.

## Submission requirements

Submit one syntactically valid operational change record containing:

- observed deployment and security configuration;
- timestamped target-health and request evidence;
- supported diagnosis and correction;
- rollback trigger and action;
- complete resource inventory;
- removed-resource IDs and final zero-resource result; and
- confirmation that Copilot input was sanitized and every generated statement was verified.

Do not submit credentials, tokens, cookies, account numbers, public addresses, personal information, or unrelated resource details.

## Completion validation

Before submission, verify that evidence was captured before teardown, all three assessed components are represented, both intended instance IDs occur in successful request observations, every inventory ID has cleanup evidence, and the final chargeable-resource count is zero.