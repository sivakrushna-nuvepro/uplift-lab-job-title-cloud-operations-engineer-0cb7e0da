# Restore and Prove a Secure Load-Balanced Application

## Purpose

Restore a two-target AWS application behind an Application Load Balancer, diagnose an unhealthy target from evidence, prove secure routing, and remove learner-created chargeable resources. Record only results you personally observe.

## Scenario

The Nuvepro GenAI Sandbox provides an existing VPC, two approved subnets, an approved application image, and scoped browser-based AWS Management Console permissions. Establish the deployment, determine why one intended target is unhealthy, correct only the supported fault, and produce a verified operational change record.

Microsoft 365 Copilot may organize sanitized observations, but it is not a source of AWS evidence. Confirm that Copilot is licensed before beginning the drafting step. Never paste credentials, account numbers, public endpoint tokens, cookies, personal information, or other secrets.

## Deployment brief

Use the supplied cards and fixtures as the authoritative task inputs:

- Application: `acme-operations-demo`
- Approved image: `ami-0acme2025001`
- Instance type: `t3.micro`
- Intended instances: `i-0acmeapp01` and `i-0acmeapp02`
- Approved subnets: `subnet-0aaa1111` and `subnet-0bbb2222`
- Load balancer: `alb-acme-ops`
- Target group: `tg-acme-app`
- Public service: HTTPS on port 443
- Application service: HTTP on port 8080
- Expected readiness response: HTTP 200 from `/ready`
- Load balancer security group: `sg-0alb001`
- Instance security group: `sg-0app001`

The existing VPC is `vpc-0acme001`. Do not replace the approved network foundations or broaden access to compensate for an unhealthy target.

## Prerequisites and cautions

1. Confirm that you can access the sandbox AWS Management Console and Microsoft 365 Copilot.
2. Open `practice_project/practice-solution/operational-change-record.template.json` in the workspace editor. This is the learner-owned deliverable.
3. Preserve the template structure and use exact observed resource identifiers.
4. Do not place AWS credentials or unsanitized console output in Copilot or the record.
5. Create only the resources required by the brief. Existing sandbox network foundations are not learner-created inventory.
6. Capture live evidence before deleting anything. Deleted resources cannot provide target-health or routing evidence.

## Guided steps

1. In EC2, inspect the approved image and launch two `t3.micro` application instances in the existing VPC. Place `i-0acmeapp01` in `subnet-0aaa1111` and `i-0acmeapp02` in `subnet-0bbb2222` as directed by the sandbox naming controls.
2. Create or select the intended target group `tg-acme-app` using HTTP port 8080 and register exactly the two intended instances.
3. Create or select `alb-acme-ops` across both approved subnets. Configure its HTTPS port 443 listener to forward by default to `tg-acme-app`.
4. Configure the load balancer security group so its public inbound rule permits only the required HTTPS service traffic on TCP port 443.
5. Configure the instance security group so TCP port 8080 is sourced from `sg-0alb001`. Do not use `0.0.0.0/0`, `::/0`, or another public CIDR for instance application ingress.
6. Wait for target-health observations. Do not immediately alter security groups, ports, health paths, or startup settings merely because one target is unhealthy.
7. Follow the diagnosis process below and make only the evidence-supported correction.
8. Wait through the configured health-check intervals until both intended targets report healthy.
9. Send repeated requests to the load balancer HTTPS endpoint. Capture six successful requests with status 200 and continue if necessary until both `i-0acmeapp01` and `i-0acmeapp02` appear in the application responses.
10. Complete the live validation, diagnosis, rollback, and inventory fields in the learner record before teardown.

Observable result: the HTTPS listener forwards to the intended HTTP target group, both intended targets are healthy, and repeated successful requests identify both instances without exposing the instance application port publicly.

Validation method: compare the listener, target-group health, security-group inbound rules, and request observations with the three supplied cards. Do not infer success from configuration alone.

## Diagnose before changing

Use a hypothesis table or equivalent notes to distinguish among path, port, protocol, response-code, startup, and network-rule explanations.

1. Record the current target-group health-check configuration before editing it.
2. Read the unhealthy target's reason code in target health.
3. Compare application-log responses for the paths that were actually requested.
4. Confirm whether port 8080 is reachable from `sg-0alb001` using the supplied network-check observation.
5. Compare these observations with the expected readiness endpoint in the deployment brief.
6. State the single cause supported by all observations and identify evidence that rules out plausible alternatives.
7. Apply the narrow correction. Do not widen instance ingress.
8. Recheck target health and record the post-change state for each intended instance.

If observations differ from the supplied incident card, stop and document the discrepancy rather than manufacturing a matching result.

## Capture evidence before teardown

Complete these parts of `practice_project/practice-solution/operational-change-record.template.json` while resources are live:

- exact instance IDs, types, and approved subnet IDs;
- listener protocol, port, load balancer ID, and default target group;
- target-group protocol, application port, corrected health-check path, and healthy status code;
- load balancer and instance security-group inbound rules;
- a timestamped health state for each intended target;
- at least six successful HTTPS request observations, collectively showing both instance IDs;
- the evidence-supported diagnosis and correction;
- a reproducible rollback trigger and rollback action;
- every learner-created EC2, load-balancer, target-group, and security-group resource ID.

Review the record for unsupported claims before cleanup. Screenshots may supplement structured observations, but screenshots do not replace the required JSON fields.

## Rollback

Define rollback before teardown. A suitable trigger must be observable, such as either intended target remaining unhealthy after the correction and propagation interval, new 5xx responses, or failure of the HTTPS listener. The action must be reproducible and safe: restore the last known working target-group setting or listener configuration, deregister failed replacement targets if appropriate, revalidate service, and avoid broadening ingress.

Do not execute rollback merely because the exercise later requires cleanup. Rollback restores service after a harmful change; cleanup removes the completed temporary deployment.

## Cleanup and final cost check

Only begin after live evidence is complete.

1. Remove or disable the HTTPS listener dependency as required by the console workflow.
2. Deregister the two targets and delete the learner-created target group when it is no longer referenced.
3. Delete the learner-created Application Load Balancer and wait for deletion to complete.
4. Terminate the two learner-created EC2 instances and confirm their terminal state.
5. Delete learner-created security groups only after network interfaces and references have been released.
6. Review EC2 instances, load balancers, target groups, network interfaces, elastic IP addresses, and other sandbox billing views for leftovers.
7. Match every ID in the created-resource inventory to the removed-resource list.
8. Record a final `remaining_chargeable_resource_count` of zero only when the console evidence supports it.

Observable result: every inventoried learner-created resource has been removed and the final sandbox check shows zero learner-created chargeable resources remaining.

Troubleshooting: if security-group deletion reports a dependency, inspect load balancer and instance network interfaces and wait for asynchronous deletion. Do not omit the security group from the inventory or falsely report zero.

## Copilot-assisted handoff

1. Sanitize the evidence before providing it to Microsoft 365 Copilot. Remove account identifiers, credentials, tokens, user data, full URLs containing sensitive values, and unrelated console details.
2. Ask Copilot to structure only the supplied facts under deployment, validation, diagnosis, correction, rollback, inventory, and cleanup headings.
3. Instruct it to mark missing evidence as unknown rather than filling gaps.
4. Transfer the useful draft wording into the learner-owned JSON record without changing observed IDs, status codes, paths, timestamps, or resource states.
5. Verify every Copilot statement against the saved AWS observations and supplied cards. Correct or remove every unsupported statement.
6. Mark the record ready for review only after the structured evidence and final cleanup result agree.

The final deliverable is the completed learner operational change record. Copilot output alone is not the deliverable and is not proof of validation.