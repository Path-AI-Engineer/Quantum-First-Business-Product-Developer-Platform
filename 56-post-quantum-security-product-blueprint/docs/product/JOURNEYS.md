# Service blueprint and customer journeys — candidate

| Journey | Frontstage user | Backstage process | Handoff / failure point |
| --- | --- | --- | --- |
| Import fixture | Architect selects a source | Validate entire batch and tag tenant/source | Reject unknown assets, secrets and malformed records without partial save |
| Triage finding | Application owner opens evidence path | Reconcile observations, preserve conflict | Missing source means verify-first, never safe |
| Plan wave | Program owner selects actions | Check ownership, dependencies and acceptance evidence | Human change board must approve before any real lab-test or migration |
| Review posture | Risk reviewer checks bands and caveats | Reconcile counts from tenant snapshot | Unknown denominator disclosed; no binary security claim |
| Export evidence | Reviewer downloads a report | Hash deterministic source summary | Production export needs watermark, retention and access logging |

Buyer: executive sponsor and security program owner. Daily users: crypto
architect, application owner and infrastructure/PKI owner. Approver: risk and
change board. Auditor: read-only external assessor. The prototype does not
replace any of these roles.

## Twelve scripted usability tasks (not human-validated)

1. Select Northstar Bank and locate total assets.
2. Switch to Aster Health and confirm only 38 assets appear.
3. Switch to Harbor Industrial and locate a vendor-dependent asset.
4. Filter inventory by a full asset ID.
5. Find a long-lived-data asset.
6. Inspect an externally exposed asset in the heatmap.
7. Open a finding and follow its source digest.
8. Identify an unknown or conflicting finding and explain why it is verify-first.
9. Locate the owner and acceptance evidence for a migration action.
10. Propose a synthetic lab wave without changing any system.
11. Generate and download an executive report; reconcile totals.
12. Switch to read-only reviewer and confirm write controls are disabled.

Automated browser checks can prove controls and navigation work. They cannot
prove real-user task success or time-to-triage; those metrics require observed
participants and consent during a pilot.
