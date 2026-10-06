# Practical Assessment: Provision and Validate EC2 Targets Behind an Application Load Balancer

## Assessment overview

Complete this 1.5-hour assessment in a fresh Nuvepro GenAI Sandbox. Work independently from the supplied Application Deployment Brief, Sandbox Network Card, and Health Evidence Card. Submit one completed copy of `practice_project/practice-solution/operational-change-record.template.json` based on evidence you observe during this assessment.

The assessment is paired with Simulation 1 but requires fresh evidence. Do not submit simulation observations as assessment results.

## Required outcome

Provision two intended EC2 application instances in the approved subnets behind the intended Application Load Balancer. Configure the HTTPS listener to route to the HTTP application target group, enforce load-balancer-only application ingress to the instances, diagnose and correct the seeded unhealthy-target condition, prove live routing, and remove all learner-created chargeable resources.

## Assessment tasks

1. Inspect the supplied cards and identify the approved image, instance size, intended target IDs, subnets, listener, target group, application port, and security-group boundaries.
2. Establish the specified two-instance deployment across the approved subnets.
3. Configure the public entry point for only the required inbound service traffic.
4. Configure instance application-port ingress to use the load balancer security group as its source. Public CIDR ingress to the instance application port is prohibited.
5. Examine target-health, application-log, and network observations. Distinguish the seeded fault from plausible port, protocol, response-code, startup, and network-rule explanations before changing configuration.
6. Apply only the evidence-supported correction and obtain healthy status for exactly the two intended targets.
7. Send at least six successful requests through the load balancer. The captured responses must collectively identify both intended instance IDs.
8. Define a reproducible rollback trigger and action tied to an observable service failure.
9. Inventory every learner-created EC2 instance, load balancer, target group, and security group.
10. Capture all live target-health, routing, and ingress evidence before teardown.
11. Remove all inventoried learner-created resources in dependency order and perform a distinct final check showing zero learner-created chargeable resources remaining.
12. Use Microsoft 365 Copilot only to structure sanitized facts. Reconcile every statement with observed AWS evidence before submission.

## Evidence sequence

The sequence is mandatory:

1. Build and diagnose.
2. Correct and wait for health-check propagation.
3. Capture live health, security, listener, and request evidence.
4. Review the live evidence for completeness.
5. Tear down learner-created resources.
6. Capture the final cleanup-to-zero evidence.

Do not tear down before capturing live evidence. A final zero-resource result cannot replace evidence that the service worked while resources were present.

## Submission requirements

Submit one valid JSON operational change record containing:

- the exact deployment configuration and resource identifiers;
- two healthy intended target observations;
- at least six successful load-balancer requests with both instance identifiers represented;
- instance ingress evidence showing the application port is sourced only from the load balancer security group;
- the supported seeded cause, applied correction, and post-correction result;
- an observable rollback trigger and reproducible rollback action;
- a complete created-resource inventory for EC2, load-balancer, target-group, and security-group categories;
- a removed-resource list covering every inventoried ID;
- final evidence of zero learner-created chargeable resources remaining;
- confirmation that Copilot inputs were sanitized and every drafted statement was verified.

## Assessment components

### Component 1: Critical live validation — GATE-1

Pass requires exactly the two intended targets healthy, at least six successful requests through the load balancer, responses from both intended instances, and instance application ingress sourced only from the load balancer security group. Failure of this component fails the assessment.

### Component 2: Diagnosis and rollback

Pass requires a diagnosis consistent with the supplied and observed health evidence, a matching narrow correction, and a reproducible rollback trigger and action. Unsupported explanations or widening instance ingress do not pass.

### Component 3: Inventory and cleanup

Pass requires all required learner-created resource categories in the inventory, removal evidence for every inventoried resource ID, and a final count of zero learner-created chargeable resources.

All three components must pass.

## Validation checklist

Before submission, confirm that the JSON parses, no required evidence array is empty, no learner placeholder remains, timestamps and IDs came from this assessment, evidence was captured before teardown, every inventory ID appears in cleanup evidence, and the final resource count is supported by the sandbox console.

## Safety and data handling

Do not paste credentials, tokens, cookies, account numbers, sensitive URLs, or unrelated customer information into Microsoft 365 Copilot. If Copilot invents or alters a result, delete or correct that statement. The learner remains accountable for every submitted claim.