# Salesforce setup — build this object, then import

Two objects. The second is optional; do it only if the first import worked and
you still have time.

## 1. Investigation_Case__c

Setup -> Object Manager -> Create -> Custom Object.
Label **Investigation Case**, Plural **Investigation Cases**, Record Name
**Work Reference** as *Text*. Tick **Allow Reports** and **Allow Search**.

Then create these fields:

| Field Label | API Name | Type |
| --- | --- | --- |
| Work Reference | `Work_Ref__c` | Text (External ID, Unique), length 40 |
| Description | `Description__c` | Long Text Area, length 5000 |
| State | `State__c` | Text, length 80 |
| Constituency | `Constituency__c` | Text, length 120 |
| Implementing Agency | `Implementing_Agency__c` | Text, length 255 |
| MP Name | `MP_Name__c` | Text, length 120 |
| Recommended Amount | `Recommended_Amount__c` | Currency (16,2) |
| Exposure | `Exposure__c` | Currency (16,2) |
| Audit ROI | `Audit_ROI__c` | Number (16,2) |
| Priority | `Priority__c` | Number (3,4) |
| Confidence Band | `Confidence_Band__c` | Picklist: HIGH, MEDIUM, LOW |
| Signal Families | `Signal_Families__c` | Number (2,0) |
| Work Type | `Work_Type__c` | Text, length 255 |
| Recommendation Date | `Recommendation_Date__c` | Date |
| Work Status | `Work_Status__c` | Picklist: Open, Completed |
| Evidence Summary | `Evidence_Summary__c` | Long Text Area, length 5000 |
| Recommended Next Step | `Recommended_Next_Step__c` | Long Text Area, length 5000 |
| Suggested Actions | `Suggested_Actions__c` | Long Text Area, length 2000 |
| Early Warning Level | `Early_Warning_Level__c` | Picklist: CRITICAL, HIGH, MEDIUM, LOW |
| Early Warning Reason | `Early_Warning_Reason__c` | Long Text Area, length 2000 |
| Compliance Findings | `Compliance_Findings__c` | Long Text Area, length 2000 |
| Escalation Tier | `Escalation_Tier__c` | Picklist: District Monitoring, State Nodal, Ministry Review |
| Target Review Date | `Target_Review_Date__c` | Date |
| Investigation Status | `Investigation_Status__c` | Picklist: New, Assigned, In Progress, Verified, Closed |
| Officer Finding | `Officer_Finding__c` | Picklist: (leave blank on import) Verified Complete, Verified In Progress, Not Started, Not Found, Record Mismatch, No Access, False Positive |
| Not A Fraud Finding | `Not_A_Fraud_Finding__c` | Checkbox (default TRUE) |

**Set `Work_Ref__c` as External ID and Unique.** It lets you re-run the import to
update rather than duplicate, which you will want the second time.

## 2. Evidence__c (optional)

| Field Label | API Name | Type |
| --- | --- | --- |
| Work Reference | `Work_Ref__c` | Text (used to relate to the case), length 40 |
| Investigation Case | `Investigation_Case__r.Work_Ref__c` | Lookup, resolved from the case's External ID at load time |
| Signal | `Signal__c` | Text, length 120 |
| Family | `Family__c` | Picklist: amount, duration, lifecycle, behaviour, multivariate, duplication |
| Detail | `Detail__c` | Long Text Area, length 5000 |

## 3. Import

Setup -> Data Import Wizard -> Custom Objects -> Investigation Cases -> Add new
records. Drop in `investigation_cases.csv`. The column headers already match the
API names, so the mapping should come up green with nothing to fix.

**If a row fails**, it is almost always one of three things: a date that is not
`YYYY-MM-DD`, a picklist value you have not created on the field yet, or a text
value longer than the field. This export controls all three, so a failure usually
means a field was created with the wrong type — check that one first.

## 4. What to say about why this is only 500 rows

> "A Developer Edition org holds about 2,500 records. We did not try to put two
> lakh works in a CRM — the models run in Python where they belong. Salesforce
> holds the cases that need a human: assignment, approval, audit, and the mobile
> app an officer uses at the site. That split is the design."

## 5. Agentforce, once the data is in

Setup -> Agentforce (or Einstein Bots if Agentforce is not in your org).

Create one agent with **one topic** — call it *Investigation Lookup*. Give it the
standard record-query actions against Investigation Case. That is enough for it to
answer:

- "Show me HIGH priority cases in Bihar"
- "Which case has the highest exposure?"
- "What is the recommended next step for MP3018356-W86316?"

**Do not build the callout to the Python API today.** Named Credentials plus Apex
plus a tunnel is where the remaining hours go. The React app already has that
assistant and it answers over all 210,993 works.
