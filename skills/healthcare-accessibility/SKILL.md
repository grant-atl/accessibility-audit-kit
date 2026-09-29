---
name: healthcare-accessibility
description: Audit, design, or remediate accessibility in healthcare portals, patient and caregiver journeys, clinician workflows, telehealth, clinical results, consent, and generated medical documents. Use when healthcare-specific care access, communication, privacy, or clinical meaning affects the work; not for medical advice or a generic page-only audit.
license: MIT
---

# Healthcare accessibility

Evaluate whether people can obtain care, understand the information presented, and act independently using their access needs. A technically accessible portal does not establish that its appointment, interpreter, consent, vendor, or document workflow works.

## Establish the care journey

Identify the requested product, roles, workflow boundaries, and test environment. Include patients, authorized caregivers/proxies, and clinicians/staff where in scope; do not assume disability implies incapacity or requires a caregiver. Map entry, every page/state, handoffs, errors, recovery, and the usable final result.

For each relevant journey, read [references/healthcare-journeys.md](references/healthcare-journeys.md). Prioritize barriers that prevent care, create a material risk of misunderstanding clinical information, undermine private communication, or block consent or records. Keep clinical risk priority separate from WCAG level and from an unproven medical outcome.

Use WCAG 2.2 AA as the engineering default unless the user specifies another target. A full audit assesses all **86 current WCAG 2.2 criteria**, with AAA findings reported separately from the **55 A/AA criteria** required for an AA target. If installed, the `accessibility-audit` skill's matrix and coverage ledger can support this work. Otherwise use the [official WCAG 2.2 criteria](https://www.w3.org/TR/WCAG22/) and maintain a local page/state/criterion ledger. This specialist skill is independently usable; it does not depend on another package being installed. Native apps and documents also need platform testing and [WCAG2ICT guidance](https://www.w3.org/TR/wcag2ict/).

## Preserve care, meaning, and privacy

- Use synthetic patients and an authorized sandbox for bookings, messages, refills, payments, signatures, and consent. An audit does not authorize real care actions, chart changes, account impersonation, or communications to clinicians.
- Preserve supplied test names, results, units, reference ranges, source timestamps, uncertainty, and clinician instructions. Improve structure and explanations without inventing diagnoses, normal ranges, dose changes, urgency, or treatment recommendations. Flag ambiguous clinical copy for the clinical owner.
- Give AT users equivalent information and choice. Avoid unnecessary sensitive information in notifications and automatic announcements, but do not strip the detail needed to distinguish patients, results, recipients, or actions. Check both audible disclosure and the ability to access the full information deliberately.
- Keep role boundaries and authentication intact. Accessible recovery, proxy access, and timeout handling must not bypass identity checks, expose another record, or store sensitive drafts insecurely.
- Keep PHI, credentials, tokens, raw recordings, real patient screenshots, and sensitive document metadata out of public findings, fixtures, commits, and uploads. Use redacted or synthetic evidence while preserving enough detail to reproduce the defect.

## Test the actual outcome

Exercise each in-scope page/state with keyboard and actual supported AT, including VoiceOver where requested. Record platform, browser/AT versions, action, focus result, and announcement. An accessibility-tree snapshot is not a screen-reader test. Also verify contrast, 200% text resize, reflow, text spacing, touch/motion behavior, alternate text, and relevant page/document metadata through the chosen WCAG criteria.

Test failed authentication, unavailable dates, invalid intake, expired sessions, lost connections, missing documents, and denied proxy permissions alongside the successful path. A vendor handoff is part of the journey. When access, specialist review, or a device is unavailable, record untested/blocked evidence; never replace it with a claimed pass. For an all-pages audit, a representative sample is incomplete coverage.

For telehealth, verify both the interface and effective communication with the person's required accommodations. Automated captions do not establish that a qualified interpreter or other communication service is unnecessary. For clinical copy and translated content, involve qualified reviewers and people with relevant access needs; one participant does not represent every disability.

## Report and remediate

For each finding provide: **role and journey; page/state; affected task; reproducible steps and actual evidence; criterion/version/level or separate usability concern; care/privacy impact; smallest shared fix and observable acceptance test**. Include unresolved coverage and third-party ownership. Retest the entire affected process after shared-component or template fixes.

Legal coverage depends on entity, jurisdiction, funding, and service. Use the official sources in the reference and verify current requirements before reporting a deadline or applicability conclusion. Do not claim WCAG conformance establishes legal, clinical-safety, or privacy certification.
