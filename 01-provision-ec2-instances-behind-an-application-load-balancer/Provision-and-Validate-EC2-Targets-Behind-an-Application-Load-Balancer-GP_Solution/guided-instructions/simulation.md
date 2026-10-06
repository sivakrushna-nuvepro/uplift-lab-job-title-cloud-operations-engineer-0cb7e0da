# Restore and Prove a Secure Load-Balanced Application

**Duration:** 1.5 hours  
**Difficulty:** Proficient  
**Requirements served:** REQ-001 and REQ-002

## Scenario

In the Nuvepro GenAI Sandbox, use the browser-based AWS Management Console to restore a secure, load-balanced application. The account provides an existing VPC, approved subnets, an approved image, and scoped permissions. You must provision two EC2 application targets behind an Application Load Balancer (ALB), diagnose one unhealthy target from evidence, prove secure routing, and remove learner-created chargeable resources.

Work only in the assigned sandbox. Do not paste account numbers, public addresses, credentials, tokens, cookies, user identities, or unrestricted console screenshots into Microsoft 365 Copilot. Confirm that the required Copilot license is available before beginning the handoff step.

## Deployment brief

Use these supplied requirements without substituting resources:

- Application: `acme-operations-demo`
- Approved image: `ami-0acme2025001`
- Instance type: `t3.micro`
- Intended targets: `i-0acmeapp01` and `i-0acmeapp02`
- Place `i-0acmeapp01` in `subnet-0aaa1111` and `i-0acmeapp02` in `subnet-0bbb2222`.
- ALB: `alb-acme-ops`, with public HTTPS listener on port 443
- Target group: `tg-acme-app`, using HTTP port 8080
- ALB security group: `sg-0alb001`
- Instance security group: `sg-0app001`
- Expected health endpoint: HTTP `GET /ready` returning status 200

The ALB security group may accept the required public TCP/443 service traffic. The instance security group must accept TCP/8080 from `sg-0alb001`, not from a public CIDR. Do not widen instance ingress while troubleshooting.

## Guided steps

1. Review the Application Deployment Brief, Sandbox Network Card, and Seeded Health-Incident Card. Create an inventory section in `reference_project/practice-solution/operational-change-record.template.json` before provisioning.
2. In EC2, launch the two approved `t3.micro` instances from `ami-0acme2025001`. Use the specified instance identities and approved subnets. Attach only the intended instance security group.
3. Configure `sg-0alb001` for the required public TCP/443 ingress. Configure `sg-0app001` with TCP/8080 sourced from `sg-0alb001`. Inspect all inbound rules and remove any public application-port rule.
4. Create or confirm `tg-acme-app` uses HTTP on port 8080. Register exactly the two intended targets.
5. Create or confirm `alb-acme-ops` spans the two approved subnets. Configure its HTTPS/443 listener to forward by default to `tg-acme-app`.
6. Wait for target-health observations. Record each target ID, state, reason, and observation time before changing any setting.
7. Follow the evidence-led diagnosis below. Change only the parameter supported by the observations, then wait for both intended targets to become healthy.
8. Request the public ALB endpoint repeatedly. Capture six successful requests with HTTP status 200 and the responding instance identifier. The six observations must collectively include both `i-0acmeapp01` and `i-0acmeapp02`.
9. Reinspect the listener, target group, target health, and both security groups. Record the observed configuration rather than merely restating the brief.

**Observable result:** exactly two intended targets are healthy, HTTPS/443 forwards to the intended target group, application traffic reaches HTTP/8080, and repeated responses identify both instances.

**Validation:** compare the live console values with the supplied cards and complete the `deployment`, `security`, and `validation` sections of the learner record.

## Diagnose before changing

Treat the incident observations as competing evidence. Determine whether the fault is caused by the target-group protocol, port, health-check path, accepted status code, application startup, or network reachability before editing the configuration.

The recorded observations show that the ALB security group can reach `i-0acmeapp02` on port 8080, `GET /healthz` returns 404, and `GET /ready` returns 200. A `Target.ResponseCodeMismatch` therefore supports a health-check request mismatch rather than a need for wider ingress. Record the cause you derived, the rejected alternatives, and the smallest supported correction. Correct the target-group health-check path from `/healthz` to `/ready` while retaining status code 200 and load-balancer-only instance ingress.

After health-check propagation, confirm both `i-0acmeapp01` and `i-0acmeapp02` report `healthy`. If they do not, stop and compare the target reason, listener action, port, protocol, application response, and security-group source with the cards. Do not make speculative changes.

## Capture evidence before teardown

Complete this section while the resources are live. Capture and timestamp:

1. Both intended target IDs and their `healthy` states.
2. The HTTPS/443 listener and its default target-group action.
3. The target group's HTTP/8080 settings, `/ready` health path, and healthy status code 200.
4. The instance security-group rule showing TCP/8080 sourced only from `sg-0alb001`.
5. Six successful endpoint requests, each with status 200 and its responding instance ID; both instance IDs must appear.
6. An inventory of every learner-created EC2 instance, load balancer, target group, and security group.

Sanitize copied observations before using them outside AWS. Prefer compact text fields over screenshots. Exclude credentials, account identifiers, session data, unrelated resource names, public addresses, and personal information.

## Rollback

Before cleanup, state a reproducible rollback trigger and action in the learner record. A suitable trigger is either target failing to become healthy after the allowed propagation interval, elevated endpoint failures, or a security validation failure after the change.

The rollback action must be specific: restore the last known approved target-group setting if safe, stop routing through the changed target group, deregister failing targets as appropriate, and revalidate the prior listener path and security posture. Rollback must never restore public TCP/8080 instance ingress. Record who would be notified and which observations determine whether service has recovered.

## Cleanup and final cost check

Cleanup begins only after all live evidence above has been captured.

1. Remove or terminate the learner-created EC2 targets and wait for termination to progress.
2. Remove the ALB listener or routing dependency, then delete the learner-created load balancer and wait until it is no longer active.
3. Delete the learner-created target group after its load-balancer dependency is gone.
4. Delete learner-created security groups only after network-interface dependencies have cleared. Do not delete shared sandbox foundations.
5. Compare every ID in the inventory with the removed-resource list.
6. Perform a final sandbox resource and cost check. Record `remaining_chargeable_resource_count` as `0` only when no learner-created chargeable resource remains.

**Observable result:** every inventoried learner-created resource is represented in cleanup evidence and the final chargeable-resource count is zero.

**Validation:** search the relevant EC2 and Elastic Load Balancing views for each inventoried ID and record the final timestamp and result.

## Copilot-assisted handoff

Provide Microsoft 365 Copilot only the sanitized facts already entered in the learner template. Ask it to organize, not infer, a concise summary with these headings: change, diagnosis, correction, target and routing validation, security validation, rollback, inventory, and cleanup.

Verify every Copilot statement against the captured AWS evidence. Correct unsupported claims, invented timestamps, unobserved health results, altered resource IDs, and any claim that cleanup succeeded without the final zero-resource check. Copilot output is a draft; the learner owns the final record.

Save the corrected content in `reference_project/practice-solution/operational-change-record.template.json`, set its status to the appropriate submitted state only after verification, and confirm that the file remains valid JSON. The final deliverable is one verified operational change record containing diagnosis, live validation, rollback, inventory, and cleanup evidence.