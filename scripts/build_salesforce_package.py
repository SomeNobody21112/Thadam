"""Generate a deployable Salesforce metadata package for the investigation workflow.

Clicking twenty-six fields into Setup takes about forty minutes and one mistyped field type
costs another ten. This writes the whole object model as Metadata API source, so the org is
built by one command instead.

What it produces: two custom objects, every field with the right type and length, the
picklist values already populated, a page layout that actually shows the fields, two list
views, tabs, a Lightning app, and a permission set.

Run:

    .venv/Scripts/python.exe scripts/build_salesforce_package.py

Then, in the generated folder:

    npm install -g @salesforce/cli
    sf org login web --alias mplads
    sf project deploy start --target-org mplads

The login opens a browser and you authenticate there. Nothing reads your password.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mplads import config  # noqa: E402

PKG = config.REPO_ROOT / "salesforce_package"
SRC = PKG / "force-app" / "main" / "default"
API_VERSION = "62.0"

XML = '<?xml version="1.0" encoding="UTF-8"?>\n'

# --------------------------------------------------------------------------- fields
#
# (api_name, label, kind, spec)
#
# Salesforce "precision" in metadata is TOTAL digits including the decimals, which is the
# single most common reason a field deploy fails. Currency(16,2) is precision 18, scale 2.

CASE_FIELDS: list[tuple[str, str, str, dict]] = [
    ("Work_Ref__c", "Work Reference", "Text",
     {"length": 40, "externalId": True, "unique": True, "required": True}),
    ("Description__c", "Description", "LongTextArea", {"length": 5000, "visibleLines": 4}),
    ("State__c", "State", "Text", {"length": 80}),
    ("Constituency__c", "Constituency", "Text", {"length": 120}),
    ("Implementing_Agency__c", "Implementing Agency", "Text", {"length": 255}),
    ("MP_Name__c", "MP Name", "Text", {"length": 120}),
    ("Recommended_Amount__c", "Recommended Amount", "Currency",
     {"precision": 18, "scale": 2}),
    ("Exposure__c", "Exposure at Risk", "Currency", {"precision": 18, "scale": 2}),
    ("Audit_ROI__c", "Audit ROI", "Number", {"precision": 18, "scale": 2}),
    ("Priority__c", "Priority", "Number", {"precision": 5, "scale": 4}),
    ("Confidence_Band__c", "Confidence Band", "Picklist",
     {"values": ["HIGH", "MEDIUM", "LOW"]}),
    ("Signal_Families__c", "Signal Families", "Number", {"precision": 2, "scale": 0}),
    ("Work_Type__c", "Work Type", "Text", {"length": 255}),
    ("Recommendation_Date__c", "Recommendation Date", "Date", {}),
    ("Work_Status__c", "Work Status", "Picklist", {"values": ["Open", "Completed"]}),
    ("Evidence_Summary__c", "Evidence Summary", "LongTextArea",
     {"length": 5000, "visibleLines": 6}),
    ("Recommended_Next_Step__c", "Recommended Next Step", "LongTextArea",
     {"length": 5000, "visibleLines": 4}),
    ("Suggested_Actions__c", "Suggested Actions", "LongTextArea",
     {"length": 2000, "visibleLines": 4}),
    ("Early_Warning_Level__c", "Early Warning Level", "Picklist",
     {"values": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]}),
    ("Early_Warning_Reason__c", "Early Warning Reason", "LongTextArea",
     {"length": 2000, "visibleLines": 3}),
    ("Compliance_Findings__c", "Compliance Findings", "LongTextArea",
     {"length": 2000, "visibleLines": 3}),
    ("Escalation_Tier__c", "Escalation Tier", "Picklist",
     {"values": ["District Monitoring", "State Nodal", "Ministry Review"]}),
    ("Target_Review_Date__c", "Target Review Date", "Date", {}),
    # Order matters: Path renders these left to right exactly as listed.
    ("Investigation_Status__c", "Investigation Status", "Picklist",
     {"values": ["New", "Assigned", "In Progress", "Verified", "Closed"],
      "default": "New"}),
    ("Officer_Finding__c", "Officer Finding", "Picklist",
     {"values": ["Verified Complete", "Verified In Progress", "Not Started",
                 "Not Found", "Record Mismatch", "No Access", "False Positive"]}),
    ("Not_A_Fraud_Finding__c", "Not A Fraud Finding", "Checkbox", {"default": "true"}),
]

EVIDENCE_FIELDS: list[tuple[str, str, str, dict]] = [
    ("Work_Ref__c", "Work Reference", "Text", {"length": 40, "required": True}),
    ("Signal__c", "Signal", "Text", {"length": 120}),
    ("Family__c", "Family", "Picklist",
     {"values": ["amount", "duration", "lifecycle", "behaviour", "multivariate",
                 "duplication"]}),
    ("Detail__c", "Detail", "LongTextArea", {"length": 5000, "visibleLines": 4}),
    ("Investigation_Case__c", "Investigation Case", "Lookup",
     {"referenceTo": "Investigation_Case__c",
      "relationshipName": "Evidence", "relationshipLabel": "Evidence"}),
]


def field_xml(api: str, label: str, kind: str, spec: dict) -> str:
    body = [f"    <fullName>{api}</fullName>", f"    <label>{escape(label)}</label>",
            f"    <type>{kind}</type>"]

    if spec.get("required"):
        body.append("    <required>true</required>")
    if spec.get("externalId"):
        body.append("    <externalId>true</externalId>")
    if spec.get("unique"):
        body.append("    <unique>true</unique>")

    if kind == "Text":
        body.append(f"    <length>{spec['length']}</length>")
    elif kind == "LongTextArea":
        body.append(f"    <length>{spec['length']}</length>")
        body.append(f"    <visibleLines>{spec.get('visibleLines', 3)}</visibleLines>")
    elif kind in {"Currency", "Number", "Percent"}:
        body.append(f"    <precision>{spec['precision']}</precision>")
        body.append(f"    <scale>{spec['scale']}</scale>")
    elif kind == "Checkbox":
        body.append(f"    <defaultValue>{spec.get('default', 'false')}</defaultValue>")
    elif kind == "Lookup":
        body.append(f"    <referenceTo>{spec['referenceTo']}</referenceTo>")
        body.append(f"    <relationshipName>{spec['relationshipName']}</relationshipName>")
        body.append(f"    <relationshipLabel>{spec['relationshipLabel']}</relationshipLabel>")
        body.append("    <deleteConstraint>SetNull</deleteConstraint>")
    elif kind == "Picklist":
        values = []
        for value in spec["values"]:
            values.append(
                "                <value>\n"
                f"                    <fullName>{escape(value)}</fullName>\n"
                f"                    <default>{str(value == spec.get('default')).lower()}</default>\n"
                f"                    <label>{escape(value)}</label>\n"
                "                </value>"
            )
        body.append(
            "    <valueSet>\n"
            "        <restricted>true</restricted>\n"
            "        <valueSetDefinition>\n"
            "            <sorted>false</sorted>\n"
            + "\n".join(values) + "\n"
            "        </valueSetDefinition>\n"
            "    </valueSet>"
        )

    return (XML + '<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            + "\n".join(body) + "\n</CustomField>\n")


def object_xml(label: str, plural: str, prefix: str, list_views: str = "") -> str:
    return (
        XML + '<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">\n'
        f"    <label>{label}</label>\n"
        f"    <pluralLabel>{plural}</pluralLabel>\n"
        "    <nameField>\n"
        f"        <label>{label} Number</label>\n"
        f"        <displayFormat>{prefix}-{{00000}}</displayFormat>\n"
        "        <type>AutoNumber</type>\n"
        "    </nameField>\n"
        "    <deploymentStatus>Deployed</deploymentStatus>\n"
        "    <sharingModel>ReadWrite</sharingModel>\n"
        "    <enableActivities>true</enableActivities>\n"
        "    <enableHistory>true</enableHistory>\n"
        "    <enableReports>true</enableReports>\n"
        "    <enableSearch>true</enableSearch>\n"
        "    <enableFeeds>true</enableFeeds>\n"
        f"{list_views}"
        "</CustomObject>\n"
    )


CASE_LIST_VIEWS = """    <listViews>
        <fullName>All_Cases</fullName>
        <columns>NAME</columns>
        <columns>Work_Ref__c</columns>
        <columns>State__c</columns>
        <columns>Confidence_Band__c</columns>
        <columns>Exposure__c</columns>
        <columns>Investigation_Status__c</columns>
        <columns>Target_Review_Date__c</columns>
        <filterScope>Everything</filterScope>
        <label>All Cases</label>
    </listViews>
    <listViews>
        <fullName>Open_High_Priority</fullName>
        <columns>NAME</columns>
        <columns>Work_Ref__c</columns>
        <columns>State__c</columns>
        <columns>Implementing_Agency__c</columns>
        <columns>Exposure__c</columns>
        <columns>Audit_ROI__c</columns>
        <columns>Escalation_Tier__c</columns>
        <columns>Investigation_Status__c</columns>
        <filterScope>Everything</filterScope>
        <filters>
            <field>Confidence_Band__c</field>
            <operation>equals</operation>
            <value>HIGH</value>
        </filters>
        <filters>
            <field>Investigation_Status__c</field>
            <operation>notEqual</operation>
            <value>Closed</value>
        </filters>
        <label>Open HIGH Priority</label>
    </listViews>
    <listViews>
        <fullName>My_Cases</fullName>
        <columns>NAME</columns>
        <columns>Work_Ref__c</columns>
        <columns>State__c</columns>
        <columns>Investigation_Status__c</columns>
        <columns>Target_Review_Date__c</columns>
        <filterScope>Mine</filterScope>
        <label>My Cases</label>
    </listViews>
"""


def layout_xml(object_api: str, sections: list[tuple[str, list[str]]]) -> str:
    blocks = []
    for heading, fields in sections:
        items = "\n".join(
            "            <layoutItems>\n"
            "                <behavior>Edit</behavior>\n"
            f"                <field>{f}</field>\n"
            "            </layoutItems>"
            for f in fields
        )
        blocks.append(
            "    <layoutSections>\n"
            "        <customLabel>true</customLabel>\n"
            "        <detailHeading>true</detailHeading>\n"
            "        <editHeading>true</editHeading>\n"
            f"        <label>{heading}</label>\n"
            "        <layoutColumns>\n"
            f"{items}\n"
            "        </layoutColumns>\n"
            "        <style>OneColumn</style>\n"
            "    </layoutSections>"
        )
    return (XML + '<Layout xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            + "\n".join(blocks) + "\n"
            "    <showEmailCheckbox>false</showEmailCheckbox>\n"
            "    <showRunAssignmentRulesCheckbox>false</showRunAssignmentRulesCheckbox>\n"
            "    <showSubmitAndAttachButton>false</showSubmitAndAttachButton>\n"
            "</Layout>\n")


def tab_xml(object_api: str, motif: str) -> str:
    return (XML + '<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            f"    <customObject>true</customObject>\n"
            f"    <motif>{motif}</motif>\n"
            "</CustomTab>\n")


def app_xml() -> str:
    return (XML + '<CustomApplication xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            "    <label>MPLADS Investigations</label>\n"
            "    <navType>Standard</navType>\n"
            "    <uiType>Lightning</uiType>\n"
            "    <formFactors>Small</formFactors>\n"
            "    <formFactors>Large</formFactors>\n"
            "    <tabs>Investigation_Case__c</tabs>\n"
            "    <tabs>Evidence__c</tabs>\n"
            "    <tabs>standard-report</tabs>\n"
            "    <tabs>standard-Dashboard</tabs>\n"
            "    <description>Investigation leads from the MPLADS intelligence engine, "
            "with the casework that follows them.</description>\n"
            "</CustomApplication>\n")


def permission_set_xml() -> str:
    """All fieldPermissions, then all objectPermissions.

    The Metadata API validates a PermissionSet against an ordered schema, so interleaving
    them — object A, its fields, object B, its fields — fails the whole deploy with
    "Element objectPermissions is duplicated at this location". They must be grouped.
    """
    targets = [
        ("Investigation_Case__c", [(f[0], f[3]) for f in CASE_FIELDS]),
        ("Evidence__c", [(f[0], f[3]) for f in EVIDENCE_FIELDS]),
    ]

    field_rows = []
    for obj, fields in targets:
        for api, spec in fields:
            # Salesforce refuses field permissions on a required field — it is always
            # visible and editable by definition, so naming it here fails the deploy.
            if spec.get("required"):
                continue
            field_rows.append(
                "    <fieldPermissions>\n"
                "        <editable>true</editable>\n"
                "        <field>" + obj + "." + api + "</field>\n"
                "        <readable>true</readable>\n"
                "    </fieldPermissions>"
            )

    object_rows = [
        "    <objectPermissions>\n"
        "        <allowCreate>true</allowCreate>\n"
        "        <allowDelete>true</allowDelete>\n"
        "        <allowEdit>true</allowEdit>\n"
        "        <allowRead>true</allowRead>\n"
        "        <modifyAllRecords>true</modifyAllRecords>\n"
        "        <object>" + obj + "</object>\n"
        "        <viewAllRecords>true</viewAllRecords>\n"
        "    </objectPermissions>"
        for obj, _ in targets
    ]

    return (XML + '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            "    <label>MPLADS Investigator</label>\n"
            "    <hasActivationRequired>false</hasActivationRequired>\n"
            + "\n".join(field_rows) + "\n"
            + "\n".join(object_rows) + "\n"
            "</PermissionSet>\n")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if PKG.exists():
        shutil.rmtree(PKG)

    write(PKG / "sfdx-project.json",
          '{\n'
          '  "packageDirectories": [{ "path": "force-app", "default": true }],\n'
          '  "name": "mplads-investigations",\n'
          '  "namespace": "",\n'
          '  "sfdcLoginUrl": "https://login.salesforce.com",\n'
          f'  "sourceApiVersion": "{API_VERSION}"\n'
          '}\n')

    written = 0
    for obj, label, plural, prefix, fields, views in [
        ("Investigation_Case__c", "Investigation Case", "Investigation Cases", "INV",
         CASE_FIELDS, CASE_LIST_VIEWS),
        ("Evidence__c", "Evidence", "Evidence", "EV", EVIDENCE_FIELDS, ""),
    ]:
        base = SRC / "objects" / obj
        write(base / f"{obj}.object-meta.xml", object_xml(label, plural, prefix, views))
        for api, flabel, kind, spec in fields:
            write(base / "fields" / f"{api}.field-meta.xml",
                  field_xml(api, flabel, kind, spec))
            written += 1

    write(SRC / "layouts" / "Investigation_Case__c-Investigation Case Layout.layout-meta.xml",
          layout_xml("Investigation_Case__c", [
              ("The Work", ["Work_Ref__c", "Description__c", "Work_Type__c",
                            "State__c", "Constituency__c", "Implementing_Agency__c",
                            "MP_Name__c", "Recommendation_Date__c", "Work_Status__c"]),
              ("Why It Was Surfaced", ["Confidence_Band__c", "Signal_Families__c",
                                       "Priority__c", "Evidence_Summary__c",
                                       "Compliance_Findings__c",
                                       "Early_Warning_Level__c",
                                       "Early_Warning_Reason__c"]),
              ("Money", ["Recommended_Amount__c", "Exposure__c", "Audit_ROI__c"]),
              ("What Happens Next", ["Investigation_Status__c", "Escalation_Tier__c",
                                     "Target_Review_Date__c",
                                     "Recommended_Next_Step__c", "Suggested_Actions__c",
                                     "Officer_Finding__c", "Not_A_Fraud_Finding__c"]),
          ]))

    write(SRC / "layouts" / "Evidence__c-Evidence Layout.layout-meta.xml",
          layout_xml("Evidence__c", [
              ("Evidence", ["Investigation_Case__c", "Work_Ref__c", "Signal__c",
                            "Family__c", "Detail__c"]),
          ]))

    write(SRC / "tabs" / "Investigation_Case__c.tab-meta.xml", tab_xml("Investigation_Case__c", "Custom18: Magnifying Glass"))
    write(SRC / "tabs" / "Evidence__c.tab-meta.xml", tab_xml("Evidence__c", "Custom19: Handsaw"))
    write(SRC / "applications" / "MPLADS_Investigations.app-meta.xml", app_xml())
    write(SRC / "permissionsets" / "MPLADS_Investigator.permissionset-meta.xml",
          permission_set_xml())

    print(f"wrote {written} field definitions across 2 objects")
    print(f"package at {PKG}")
    print("\nNext, in that folder:")
    print("  npm install -g @salesforce/cli")
    print("  sf org login web --alias mplads")
    print("  sf project deploy start --target-org mplads")


if __name__ == "__main__":
    main()
