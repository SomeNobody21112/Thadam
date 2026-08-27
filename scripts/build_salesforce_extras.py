"""Second Salesforce package: the Path, compact layout, reports and a dashboard.

Kept separate from the object package on purpose. These depend on the objects existing and
on org features that may or may not be switched on, so a failure here must not be able to
roll back a working object deploy.

Run after the objects are in:

    .venv/Scripts/python.exe scripts/build_salesforce_extras.py
    cd salesforce_extras
    sf project deploy start --source-dir force-app --target-org mplads
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mplads import config  # noqa: E402

PKG = config.REPO_ROOT / "salesforce_extras"
SRC = PKG / "force-app" / "main" / "default"
API_VERSION = "62.0"
XML = '<?xml version="1.0" encoding="UTF-8"?>\n'

OBJECT = "Investigation_Case__c"
REPORT_TYPE = "Investigation_Case__c"
FOLDER = "MPLADS_Reports"

#: What an officer needs on screen at each stage, and the one sentence that says why they
#: are at this stage. Guidance that restates the stage name teaches nobody anything, so
#: each of these says what the stage is *for*.
PATH_STEPS = [
    ("New", ["Confidence_Band__c", "Exposure__c", "Escalation_Tier__c"],
     "Surfaced by the intelligence engine and not yet looked at by a person. "
     "Read the evidence before deciding whether it warrants a visit."),
    ("Assigned", ["OwnerId", "Target_Review_Date__c", "Recommended_Next_Step__c"],
     "An officer owns this case. The review date is the commitment, not a suggestion."),
    ("In Progress", ["Suggested_Actions__c", "Early_Warning_Reason__c"],
     "Records requested or a site visit arranged. Log what you find in Chatter as you "
     "go, so the case explains itself to whoever reads it next."),
    ("Verified", ["Officer_Finding__c", "Not_A_Fraud_Finding__c"],
     "Someone has actually looked. Record what was found - including 'nothing wrong', "
     "which is as useful to the system as a confirmed problem."),
    ("Closed", ["Officer_Finding__c"],
     "Finding recorded and the case is done. It is now a label the engine can learn "
     "from, which is the only way the scoring ever stops being a reasoned guess."),
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def path_assistant() -> str:
    steps = []
    for value, fields, info in PATH_STEPS:
        field_rows = "\n".join(f"        <fieldNames>{f}</fieldNames>" for f in fields)
        steps.append(
            "    <pathAssistantSteps>\n"
            f"{field_rows}\n"
            f"        <info>&lt;p&gt;{info}&lt;/p&gt;</info>\n"
            f"        <picklistValueName>{value}</picklistValueName>\n"
            "    </pathAssistantSteps>"
        )
    return (XML + '<PathAssistant xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            "    <active>true</active>\n"
            f"    <entityName>{OBJECT}</entityName>\n"
            "    <fieldName>Investigation_Status__c</fieldName>\n"
            "    <masterLabel>Investigation Path</masterLabel>\n"
            "    <recordTypeName>__MASTER__</recordTypeName>\n"
            + "\n".join(steps) + "\n"
            "</PathAssistant>\n")


def compact_layout() -> str:
    """What shows in the highlights panel: who, how much, how sure, by when."""
    fields = ["Work_Ref__c", "State__c", "Exposure__c", "Confidence_Band__c",
              "Escalation_Tier__c", "Target_Review_Date__c"]
    rows = "\n".join(f"    <fields>{f}</fields>" for f in fields)
    return (XML + '<CompactLayout xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            "    <fullName>Investigation_Highlights</fullName>\n"
            f"{rows}\n"
            "    <label>Investigation Highlights</label>\n"
            "</CompactLayout>\n")


def report_folder() -> str:
    return (XML + '<ReportFolder xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            "    <folderShares>\n"
            "        <accessLevel>Manage</accessLevel>\n"
            "        <sharedTo>AllInternalUsers</sharedTo>\n"
            "        <sharedToType>Organization</sharedToType>\n"
            "    </folderShares>\n"
            "    <name>MPLADS Reports</name>\n"
            "</ReportFolder>\n")


def exposure_by_state_report() -> str:
    return (XML + '<Report xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            "    <chart>\n"
            "        <backgroundColor1>#FFFFFF</backgroundColor1>\n"
            "        <backgroundColor2>#FFFFFF</backgroundColor2>\n"
            "        <backgroundFadeDir>Diagonal</backgroundFadeDir>\n"
            "        <chartSummaries>\n"
            "            <aggregate>Sum</aggregate>\n"
            "            <axisBinding>y</axisBinding>\n"
            "            <column>Investigation_Case__c.Exposure__c</column>\n"
            "        </chartSummaries>\n"
            "        <chartType>VerticalColumn</chartType>\n"
            "        <enableHoverLabels>true</enableHoverLabels>\n"
            "        <expandOthers>true</expandOthers>\n"
            "        <groupingColumn>Investigation_Case__c.State__c</groupingColumn>\n"
            "        <location>CHART_BOTTOM</location>\n"
            "        <showAxisLabels>true</showAxisLabels>\n"
            "        <showPercentage>false</showPercentage>\n"
            "        <showTotal>false</showTotal>\n"
            "        <showValues>true</showValues>\n"
            "        <size>Medium</size>\n"
            "        <summaryAxisRange>Auto</summaryAxisRange>\n"
            "        <textColor>#000000</textColor>\n"
            "        <textSize>12</textSize>\n"
            "        <title>Exposure at Risk by State</title>\n"
            "        <titleColor>#000000</titleColor>\n"
            "        <titleSize>18</titleSize>\n"
            "    </chart>\n"
            "    <columns><field>CUST_NAME</field></columns>\n"
            "    <columns><field>Investigation_Case__c.Work_Ref__c</field></columns>\n"
            "    <columns><field>Investigation_Case__c.Confidence_Band__c</field></columns>\n"
            "    <columns><field>Investigation_Case__c.Implementing_Agency__c</field></columns>\n"
            "    <columns>\n"
            "        <aggregateTypes>Sum</aggregateTypes>\n"
            "        <field>Investigation_Case__c.Exposure__c</field>\n"
            "    </columns>\n"
            "    <columns><field>Investigation_Case__c.Investigation_Status__c</field></columns>\n"
            "    <columns><field>Investigation_Case__c.Escalation_Tier__c</field></columns>\n"
            "    <format>Summary</format>\n"
            "    <groupingsDown>\n"
            "        <dateGranularity>Day</dateGranularity>\n"
            "        <field>Investigation_Case__c.State__c</field>\n"
            "        <sortOrder>Asc</sortOrder>\n"
            "    </groupingsDown>\n"
            "    <name>Exposure by State</name>\n"
            "    <params>\n"
            "        <name>co</name>\n"
            "        <value>1</value>\n"
            "    </params>\n"
            "    <reportType>CustomEntity$Investigation_Case__c</reportType>\n"
            "    <scope>organization</scope>\n"
            "    <showDetails>true</showDetails>\n"
            "    <showGrandTotal>true</showGrandTotal>\n"
            "    <showSubTotals>true</showSubTotals>\n"
            "    <timeFrameFilter>\n"
            "        <dateColumn>CUST_CREATED_DATE</dateColumn>\n"
            "        <interval>INTERVAL_CUSTOM</interval>\n"
            "    </timeFrameFilter>\n"
            "</Report>\n")


def cases_by_tier_report() -> str:
    return (XML + '<Report xmlns="http://soap.sforce.com/2006/04/metadata">\n'
            "    <chart>\n"
            "        <backgroundColor1>#FFFFFF</backgroundColor1>\n"
            "        <backgroundColor2>#FFFFFF</backgroundColor2>\n"
            "        <backgroundFadeDir>Diagonal</backgroundFadeDir>\n"
            "        <chartSummaries>\n"
            "            <axisBinding>y</axisBinding>\n"
            "            <column>RowCount</column>\n"
            "        </chartSummaries>\n"
            "        <chartType>Donut</chartType>\n"
            "        <enableHoverLabels>true</enableHoverLabels>\n"
            "        <expandOthers>true</expandOthers>\n"
            "        <groupingColumn>Investigation_Case__c.Escalation_Tier__c</groupingColumn>\n"
            "        <legendPosition>Right</legendPosition>\n"
            "        <location>CHART_BOTTOM</location>\n"
            "        <showAxisLabels>true</showAxisLabels>\n"
            "        <showPercentage>true</showPercentage>\n"
            "        <showTotal>true</showTotal>\n"
            "        <showValues>true</showValues>\n"
            "        <size>Medium</size>\n"
            "        <summaryAxisRange>Auto</summaryAxisRange>\n"
            "        <textColor>#000000</textColor>\n"
            "        <textSize>12</textSize>\n"
            "        <title>Cases by Escalation Tier</title>\n"
            "        <titleColor>#000000</titleColor>\n"
            "        <titleSize>18</titleSize>\n"
            "    </chart>\n"
            "    <columns><field>CUST_NAME</field></columns>\n"
            "    <columns><field>Investigation_Case__c.Work_Ref__c</field></columns>\n"
            "    <columns><field>Investigation_Case__c.State__c</field></columns>\n"
            "    <columns>\n"
            "        <aggregateTypes>Sum</aggregateTypes>\n"
            "        <field>Investigation_Case__c.Exposure__c</field>\n"
            "    </columns>\n"
            "    <columns><field>Investigation_Case__c.Investigation_Status__c</field></columns>\n"
            "    <format>Summary</format>\n"
            "    <groupingsDown>\n"
            "        <dateGranularity>Day</dateGranularity>\n"
            "        <field>Investigation_Case__c.Escalation_Tier__c</field>\n"
            "        <sortOrder>Asc</sortOrder>\n"
            "    </groupingsDown>\n"
            "    <name>Cases by Escalation Tier</name>\n"
            "    <params>\n"
            "        <name>co</name>\n"
            "        <value>1</value>\n"
            "    </params>\n"
            "    <reportType>CustomEntity$Investigation_Case__c</reportType>\n"
            "    <scope>organization</scope>\n"
            "    <showDetails>true</showDetails>\n"
            "    <showGrandTotal>true</showGrandTotal>\n"
            "    <showSubTotals>true</showSubTotals>\n"
            "    <timeFrameFilter>\n"
            "        <dateColumn>CUST_CREATED_DATE</dateColumn>\n"
            "        <interval>INTERVAL_CUSTOM</interval>\n"
            "    </timeFrameFilter>\n"
            "</Report>\n")


def main() -> None:
    if (PKG / "force-app").exists():
        shutil.rmtree(PKG / "force-app")

    write(PKG / "sfdx-project.json",
          '{\n'
          '  "packageDirectories": [{ "path": "force-app", "default": true }],\n'
          '  "name": "mplads-extras",\n'
          '  "namespace": "",\n'
          '  "sfdcLoginUrl": "https://login.salesforce.com",\n'
          f'  "sourceApiVersion": "{API_VERSION}"\n'
          '}\n')

    write(SRC / "pathAssistants" / "Investigation_Path.pathAssistant-meta.xml",
          path_assistant())

    write(SRC / "objects" / OBJECT / "compactLayouts"
          / "Investigation_Highlights.compactLayout-meta.xml", compact_layout())

    # Reports metadata
    write(SRC / "reports" / f"{FOLDER}-meta.xml", report_folder())
    write(SRC / "reports" / FOLDER / "Exposure_by_State.report-meta.xml", exposure_by_state_report())
    write(SRC / "reports" / FOLDER / "Cases_by_Escalation_Tier.report-meta.xml", cases_by_tier_report())

    print(f"package at {PKG}")
    print("deploy with:")
    print(f"  cd {PKG.name}")
    print("  sf project deploy start --source-dir force-app --target-org mplads")


if __name__ == "__main__":
    main()

