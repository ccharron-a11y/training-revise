"""Expand data.xml of the QA/QC Field Documentation Training SCORM package.

Usage: python3 -I build_content.py <path to data.xml>
Edits the file in place. Idempotency is not attempted: run against the baseline.
"""
import random
import re
import string
import sys

path = sys.argv[1]
xml = open(path, encoding="utf-8").read()

random.seed(20261012)
_used = set(re.findall(r"uid=['\"]([^'\"]+)['\"]", xml))
_ALPH = string.ascii_letters + string.digits + "_-"


def uid():
    while True:
        u = random.choice(string.ascii_letters) + "".join(random.choice(_ALPH) for _ in range(9))
        if u not in _used:
            _used.add(u)
            return u


datasets = []


def hero():
    return (f"<block.grid uid='{uid()}' size=\"fullwidth\"><cmp.hero uid='{uid()}'>"
            f"<cmp.heading uid='{uid()}' level=\"1\"><![CDATA[{{{{pageTitle}}}}]]></cmp.heading>"
            f"</cmp.hero></block.grid>")


def text(html):
    return (f"<block.grid uid='{uid()}' size=\"restrict\"><cmp.text uid='{uid()}'>"
            f"<![CDATA[{html}]]></cmp.text></block.grid>")


def h2text(heading, html):
    if not html:
        return (f"<block.grid uid='{uid()}' size=\"restrict\"><cmp.heading uid='{uid()}' level=\"2\">"
                f"<![CDATA[{heading}]]></cmp.heading></block.grid>")
    return (f"<block.grid uid='{uid()}' size=\"restrict\"><cmp.stack uid='{uid()}' direction=\"v\" "
            f"space=\"xs\" classlist=\"heading-and-text\"><cmp.heading uid='{uid()}' level=\"2\">"
            f"<![CDATA[{heading}]]></cmp.heading><cmp.text uid='{uid()}'><![CDATA[{html}]]>"
            f"</cmp.text></cmp.stack></block.grid>")


def h3text(heading, html):
    return (f"<block.grid uid='{uid()}' size=\"restrict\"><cmp.stack uid='{uid()}' direction=\"v\" "
            f"space=\"xs\" classlist=\"heading-and-text\"><cmp.heading uid='{uid()}' level=\"3\">"
            f"<![CDATA[{heading}]]></cmp.heading><cmp.text uid='{uid()}'><![CDATA[{html}]]>"
            f"</cmp.text></cmp.stack></block.grid>")


def lst(items, ordered=True, checklist=False):
    if not ordered and not checklist:
        return text("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
    ds = uid()
    body = "".join(
        f"<item><title><![CDATA[Item {i + 1}]]></title><content><![CDATA[<p>{it}</p>]]></content>"
        f"<options  /><popup  /><thumbnail type=\"none\"></thumbnail></item>"
        for i, it in enumerate(items))
    datasets.append(f"<dataset uid=\"{ds}\" type=\"sr\" name=\"Select and reveal\" >{body}</dataset>")
    ltype, style, shape = ("list-ordered", "decimal", "circle") if ordered else ("list-unordered", "bullet", "none")
    return (f"<block.grid uid='{uid()}' size=\"restrict\"><cmp.list uid='{uid()}' listtype=\"{ltype}\" "
            f"itemstyle=\"{style}\" itemshape=\"{shape}\" checklist=\"{'true' if checklist else 'false'}\" "
            f"dataset=\"{ds}\"></cmp.list></block.grid>")


def table(headers, rows):
    th = "".join(f"<th>{h}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<figure class=\"table\"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></figure>"


def section(*blocks):
    return f"<section uid='{uid()}'>{''.join(blocks)}</section>"


def page(title, *sections):
    pid = uid()
    return (f"<page type=\"md\" cmp=\"standard_md\" group=\"CTc3HvvSUE\" retainscroll=\"true\" "
            f"completionpoint=\"false\" classlist=\"\" labels=\"\"  uid=\"{pid}\" id=\"{pid}\" "
            f"title=\"{title}\" references=\"\" ><settings /><sections>{''.join(sections)}</sections></page>")


EXAMPLES_NOTE = ("<p><em>Note: Section, article, paragraph, sheet and detail numbers in this course are "
                 "illustrative examples. Always cite from your own project's current documents.</em></p>")

# ---------------------------------------------------------------- new pages

p_facts = page(
    "Facts, Not Opinions",
    section(
        hero(),
        text("<p>Our value in the field comes from one thing: <strong>credibility</strong>. Every time we "
             "raise an issue, the General Contractor and subcontractors decide whether to act on it. An opinion "
             "invites a debate. A fact backed by the contract documents ends one.</p>"
             "<p><strong>The GC and subs can argue with an opinion. They cannot argue with a fact.</strong></p>"),
    ),
    section(
        h2text("What Counts as a Fact?",
               "<p>In commissioning, a fact is an observed, verifiable condition that you can compare against a "
               "written requirement. Before you raise anything as a deficiency, put it through the three-question "
               "Fact Test:</p>"),
        lst([
            "<strong>Can I cite it?</strong> Can I point to the specific document, section and paragraph (or sheet "
            "and detail) that requires something different?",
            "<strong>Can I show it?</strong> Do I have objective evidence, such as a photo, measurement, nameplate, "
            "reading or trend, that shows the condition?",
            "<strong>Would anyone reach the same conclusion?</strong> If another commissioning agent read the same "
            "paragraph and looked at the same condition, would they agree it does not comply?",
        ]),
        text("<p>If the answer to all three is <strong>yes</strong>, you have a fact-based issue. If the answer to "
             "question 1 is <strong>no</strong>, you have an opinion. It may still be a good one, but it is not a "
             "contract deficiency, and it must not be presented as one.</p>"),
    ),
    section(
        h2text("Opinion vs. Fact: Side by Side",
               "<p>The same field observation can be stated as an opinion or as a fact. Notice that the fact-based "
               "version names the location, describes the condition objectively, and cites the requirement.</p>"
               + table(
                   ["Opinion-based (avoid)", "Fact-based (use)"],
                   [
                       ["\"This insulation job looks bad.\"",
                        "\"AHU-2 supply duct, Level 3 mech room: approx. 6 ft of duct downstream of the discharge "
                        "plenum is uninsulated. Not IAW Spec 23 07 13, 3.2.A.\""],
                       ["\"That's not how we did it on the last project.\"",
                        "\"Strainer upstream of CV-4 not installed. Contrary to Drawing M-501, Detail 3 (Rev 2), "
                        "which shows a strainer with blow-down valve upstream of each coil control valve.\""],
                       ["\"That panel is too close to the wall.\"",
                        "\"Working space in front of panel LP-2A measured 30 in. Not IAW NFPA 70 (NEC) 110.26(A)(1), "
                        "which requires a 36 in. minimum depth for this condition (edition as adopted by the AHJ).\""],
                       ["\"The valve looks backwards.\"",
                        "\"Flow arrow on CHW control valve CV-3 at AHU-1 points against the direction of flow. Not "
                        "IAW manufacturer installation instructions (IOM p. 4) as required by Spec 23 09 23, 3.3.B.\""],
                       ["\"These guys don't know what they're doing.\"",
                        "Never write this. Describe the <strong>condition</strong>, never the <strong>person</strong>."],
                   ])
               + EXAMPLES_NOTE),
    ),
    section(
        h2text("Where Opinions Belong",
               "<p>Experience matters. Your opinion, based on years in the field, is often right, and the owner "
               "may want to hear it. But it must be <strong>labeled honestly</strong> and routed to the right "
               "people:</p>"),
        lst([
            "<strong>Deficiency / Issue</strong>: does not meet a written requirement. Assigned to the responsible "
            "contractor. Must include a citation.",
            "<strong>Observation</strong>: a condition worth tracking that you cannot yet tie to a requirement, or "
            "cannot yet verify. Stated neutrally, without assigning fault.",
            "<strong>Recommendation</strong>: your professional opinion or a best practice that goes beyond the "
            "contract documents. Routed to the owner and design team for a decision, <em>not</em> assigned to the "
            "contractor as a deficiency.",
        ], ordered=False),
        text("<p>Use a clear label so no one confuses the two, for example: <em>\"Recommendation (not a contract "
             "requirement): Consider adding isolation valves at each VAV reheat coil to simplify future "
             "maintenance. Owner and EOR to decide.\"</em></p>"
             "<p>Presenting an opinion as a requirement is the fastest way to lose credibility. Once a contractor "
             "catches one unsupported \"requirement,\" they will question every issue you write after it.</p>"),
    ),
)

p_cite = page(
    "Finding and Citing the Requirement",
    section(
        hero(),
        text("<p>A fact-based issue is only as strong as its citation. \"Per spec\" or \"per code\" is not a "
             "citation. It sends the contractor on a scavenger hunt and signals that you may not have looked it up "
             "yourself. A proper citation points to the exact sentence that governs the condition.</p>"),
    ),
    section(
        h2text("Know Where Requirements Live",
               "<p>Requirements come from several sources. Know them, and know which one governs:</p>"),
        lst([
            "<strong>Specifications</strong>: the written requirements, organized by CSI MasterFormat division and "
            "section.",
            "<strong>Drawings</strong>: plans, sections, details, schedules, keynotes and general notes.",
            "<strong>Addenda, ASIs, Bulletins and Change Orders</strong>: these modify the original documents. A "
            "requirement you cite may have been changed.",
            "<strong>RFI Responses</strong>: the design team's clarifications. Check for one before you write an "
            "issue on a condition that might have already been answered.",
            "<strong>Approved Submittals</strong>: what the contractor committed to install, including approved "
            "deviations.",
            "<strong>Manufacturer Installation Instructions (IOMs)</strong>: usually made enforceable by the spec "
            "(e.g., \"install in accordance with manufacturer's written instructions\"). Cite both.",
            "<strong>Owner's Project Requirements (OPR), Basis of Design (BOD) and Owner Design Standards</strong>: "
            "the owner's intent and program standards.",
            "<strong>Referenced Codes and Standards</strong>: cite the edition adopted by the Authority Having "
            "Jurisdiction (AHJ) or referenced in the spec, not simply the newest edition.",
        ], ordered=False),
        text("<p>When documents conflict, the project's <strong>order of precedence</strong> clause (typically in "
             "the General Conditions or Division 01) decides which one governs. Read it on every project. Do not "
             "assume.</p>"),
    ),
    section(
        h2text("Anatomy of a Spec Citation",
               "<p>Specifications follow a consistent structure. Learn to read it so you can cite down to the "
               "paragraph:</p>"
               + table(
                   ["Level", "Example", "What it tells you"],
                   [
                       ["Division", "23", "HVAC"],
                       ["Section", "23 07 13", "Duct Insulation"],
                       ["Part", "Part 3", "Part 1 General (submittals, QA), Part 2 Products, Part 3 Execution "
                                          "(installation, field quality control)"],
                       ["Article", "3.2", "Installation, general"],
                       ["Paragraph / Subparagraph", "A.1", "The exact requirement"],
                   ])
               + "<p>Written out, that is: <strong>Spec 23 07 13, 3.2.A.1</strong>. Most field installation "
                 "issues will be found in <strong>Part 3 – Execution</strong>.</p>"),
    ),
    section(
        h2text("Weak vs. Strong Citations",
               table(
                   ["Weak (avoid)", "Strong (use)"],
                   [
                       ["\"Per spec\"", "\"Spec 23 05 53, 3.1.B\""],
                       ["\"Per the drawings\"", "\"Drawing M-102 (Rev 4), Keynote 7\""],
                       ["\"Per code\"", "\"NFPA 70 (NEC) 110.26(A)(1), 2020 edition as adopted by the AHJ\""],
                       ["\"Industry standard\"", "\"SMACNA HVAC Duct Construction Standards, as referenced in Spec "
                                                 "23 31 13, 1.4.A\""],
                       ["\"Per the submittal\"", "\"Approved submittal 23 09 23-004, p. 12, wiring diagram\""],
                       ["\"The manufacturer says so\"", "\"Manufacturer IOM, Section 5.3, as required by Spec 23 21 "
                                                        "13, 3.1.A\""],
                   ])
               + EXAMPLES_NOTE),
    ),
    section(
        h2text("Citation Habits of a Professional",
               ""),
        lst([
            "<strong>Quote the requirement.</strong> Include the key sentence in quotation marks so the reader does "
            "not have to look it up to understand the issue.",
            "<strong>Include the revision.</strong> Cite the current sheet revision or addendum. Citing a superseded "
            "document undermines the whole issue.",
            "<strong>Check for changes.</strong> Before citing, confirm no RFI, ASI, bulletin or approved deviation "
            "has modified the requirement.",
            "<strong>Cite the most specific source.</strong> If a detail on the drawing and a general spec paragraph "
            "both apply, cite both, starting with the most specific.",
            "<strong>If you cannot find it, say so.</strong> If you believe something is wrong but cannot find the "
            "requirement, log it as an Observation or ask the design team. Do not invent a requirement.",
        ]),
    ),
)

p_statement = page(
    "Writing the Issue Statement: Not IAW / Contrary To",
    section(
        hero(),
        text("<p>Every issue should be written so that someone who has never been to the site can read it, "
             "find the location, understand exactly what is wrong, see the requirement it violates, and know what "
             "\"fixed\" looks like. The standard phrasing we use to tie a condition to a requirement is "
             "<strong>Not IAW</strong> (Not In Accordance With) or <strong>Contrary to</strong>.</p>"),
    ),
    section(
        h2text("The Issue Formula",
               "<p>Build every issue statement from the same five parts, in the same order:</p>"),
        lst([
            "<strong>Location and Equipment</strong>: building, level, room or gridline, and equipment tag. "
            "<em>\"Level 2, Room 214, VAV-2-14\"</em>",
            "<strong>Observed Condition</strong>: what you saw or measured, objectively, with units. "
            "<em>\"Discharge air temperature sensor not installed.\"</em>",
            "<strong>Requirement</strong>: Not IAW / Contrary to the specific citation, with the key language "
            "quoted. <em>\"Not IAW Spec 23 09 23, 3.4.C: 'Provide discharge air temperature sensor at each VAV "
            "box with reheat.'\"</em>",
            "<strong>Required Action</strong>: what condition will bring it into compliance. "
            "<em>\"Install DAT sensor per the cited paragraph and the approved controls submittal.\"</em>",
            "<strong>Evidence</strong>: attached photos (wide and close-up), readings or screenshots. "
            "<em>\"See Photos 1–2.\"</em>",
        ]),
    ),
    section(
        h2text("Choosing the Right Phrase",
               table(
                   ["Phrase", "Use when…", "Example"],
                   [
                       ["<strong>Not IAW ___</strong>",
                        "The installed or operating condition does not match what a document requires.",
                        "\"Pipe label missing on CHWS at AHU-3. Not IAW Spec 23 05 53, 3.4.A.\""],
                       ["<strong>Contrary to ___</strong>",
                        "The condition directly conflicts with, or does what the document prohibits.",
                        "\"Flexible duct run measured 9 ft. Contrary to Spec 23 33 00, 3.5.B: 'Flexible duct "
                        "runs shall not exceed 5 ft.'\""],
                       ["<strong>Deviates from approved submittal ___</strong>",
                        "The installed product or configuration differs from what was approved.",
                        "\"Installed pump motor nameplate 7.5 HP. Deviates from approved submittal 23 21 23-002, "
                        "which lists 10 HP.\""],
                       ["<strong>Not installed / not provided as required by ___</strong>",
                        "A required item is missing.",
                        "\"Isolation valves not provided at coil connections as required by Drawing M-501, "
                        "Detail 2.\""],
                       ["<strong>Unable to verify ___ as required by ___</strong>",
                        "You cannot confirm compliance (no access, no documentation, system not running). This "
                        "is an open item, not a confirmed deficiency.",
                        "\"Unable to verify duct leakage test results required by Spec 23 31 13, 3.6.A. Test "
                        "report not provided.\""],
                   ])
               + EXAMPLES_NOTE),
    ),
    section(
        h2text("Putting It Together",
               "<p><strong>Before</strong> (opinion-based):</p>"
               "<p><em>\"Sensor missing on VAV. Needs to be fixed ASAP.\"</em></p>"
               "<p><strong>After</strong> (fact-based):</p>"
               "<p><em>\"Level 2, Room 214, VAV-2-14: Discharge air temperature sensor not installed. Not IAW Spec "
               "23 09 23, 3.4.C: 'Provide discharge air temperature sensor at each VAV box with reheat.' Required "
               "action: Install DAT sensor per Spec 23 09 23 and approved submittal 23 09 23-004, verify point "
               "reads correctly at the BAS front end, and notify CxA for re-inspection. See Photos 1–2.\"</em></p>"
               "<p>The second version can be assigned, priced, fixed and closed without a single phone call. That "
               "is the goal.</p>"),
    ),
    section(
        h2text("Writing Rules",
               ""),
        lst([
            "<strong>Describe the condition, not the person.</strong> No blame, sarcasm or judgment.",
            "<strong>Use numbers and units.</strong> \"Measured 30 in.\" beats \"too close.\" \"Reading 58°F vs. "
            "55°F setpoint\" beats \"running warm.\"",
            "<strong>One deficiency per issue.</strong> If the same deficiency occurs at multiple identical "
            "locations, list each location (or follow the project's systemic-issue convention).",
            "<strong>Avoid absolutes and emotion.</strong> No \"never,\" \"always,\" \"terrible,\" ALL CAPS or "
            "exclamation points.",
            "<strong>Use tags exactly as they appear on the drawings and equipment schedules.</strong> So the "
            "issue can be searched, sorted and found.",
            "<strong>Read it back.</strong> Before saving, ask: could someone who was not with me find this, "
            "understand it and fix it?",
        ], ordered=False),
    ),
)

p_create = page(
    "Creating and Cross-Referencing Issues",
    section(
        hero(),
        text("<p>A well-written issue that cannot be found, or that duplicates three others, still slows the "
             "project down. How you create and connect issues in the issues platform (e.g., Cx Alloy) matters as "
             "much as how you write them.</p>"),
    ),
    section(
        h2text("Before You Create: Search First",
               "<p>Before logging a new issue, search the platform for the equipment tag and location. Ask:</p>"),
        lst([
            "Is this condition already logged as an open issue? If so, add your new photos and comments to the "
            "existing issue instead of creating a duplicate.",
            "Was this issue previously closed? If the condition has come back, create a new issue that references "
            "the closed one (see below).",
            "Is there an RFI, ASI or approved deviation that already addresses this condition?",
        ], ordered=False),
    ),
    section(
        h2text("Complete Every Field",
               "<p>Every issue should include, at minimum:</p>"
               + table(
                   ["Field", "Standard"],
                   [
                       ["Title", "<strong>[Equipment tag] – [Short condition]</strong>, e.g., <em>\"AHU-2 – "
                                 "Discharge duct insulation missing\"</em>. Searchable and specific."],
                       ["Equipment / Asset", "Linked to the correct asset in the platform."],
                       ["Location", "Building, level, room and/or gridline."],
                       ["Description", "The full issue statement: condition, Not IAW / Contrary to citation, "
                                       "required action."],
                       ["Source", "The checklist line item or functional test step that failed, e.g., "
                                  "<em>\"FPT-AHU-2, Step 14\"</em>."],
                       ["Responsible Party", "The contractor responsible for the work, or the GC."],
                       ["Priority", "P0–P3 per Spec 01 40 00 (see the Issue Classification page)."],
                       ["Due Date", "Aligned with the priority's required resolution time."],
                       ["Attachments", "Wide and close-up photos with markups, readings, screenshots."],
                   ])),
    ),
    section(
        h2text("Referencing Other Issues and Documents",
               "<p>Use consistent language to tie issues together so the history is clear:</p>"
               + table(
                   ["Situation", "How to reference it"],
                   [
                       ["Related condition on the same system",
                        "<em>\"Related to Issue #1042 (AHU-2 CHW valve actuator).\"</em>"],
                       ["Condition has come back after closure",
                        "<em>\"Repeat of Issue #0987, closed 06/14. Condition has recurred.\"</em> Do not reopen "
                        "the old issue without the project's direction; reference it."],
                       ["Duplicate logged by mistake",
                        "Close the duplicate as <em>\"Duplicate of Issue #1042\"</em> and move any unique photos or "
                        "comments to the parent issue."],
                       ["Same deficiency at many locations (systemic)",
                        "Create a parent issue describing the systemic condition and list or link each instance, "
                        "per the project's convention."],
                       ["Waiting on a design answer",
                        "<em>\"Pending RFI #087. Issue remains open until the EOR responds.\"</em>"],
                       ["Requirement was changed",
                        "<em>\"Requirement modified by ASI #12, dated 05/02.\"</em>"],
                   ])),
    ),
    section(
        h2text("Keep the Record Honest",
               ""),
        lst([
            "Add updates as new, dated comments. Do not overwrite the original description in a way that changes "
            "its meaning.",
            "Never close an issue without verification (re-inspection, Delta Walk or retest).",
            "When a contractor provides a document that resolves the issue (e.g., an RFI response or approved "
            "deviation), cite it in the closing comment.",
        ], ordered=False),
    ),
)

p_solution = page(
    "Defining the Solution",
    section(
        hero(),
        text("<p>An issue without a path to closure is just a complaint. Every issue we write must answer the "
             "contractor's next question: <strong>\"What do you need me to do to close this?\"</strong></p>"),
    ),
    section(
        h2text("State What Compliance Looks Like",
               "<p>The required action should describe the <strong>end condition</strong> that satisfies the "
               "cited requirement, and how it will be verified. For example:</p>"
               "<p><em>\"Install duct insulation on AHU-2 discharge duct per Spec 23 07 13, 3.2.A. Notify CxA when "
               "complete for re-inspection.\"</em></p>"),
    ),
    section(
        h2text("Stay in Your Lane: What vs. How",
               "<p>Our role is to define <strong>what</strong> compliance looks like, based on the documents. "
               "<strong>How</strong> the contractor achieves it (means and methods) is their responsibility, "
               "unless the documents specify the method. Telling a contractor how to do their work can shift "
               "responsibility onto us and the owner.</p>"),
    ),
    section(
        h2text("When the Documents Are Unclear, Conflicting or Silent",
               "<p>Do not fill the gap with your opinion. Instead:</p>"),
        lst([
            "<strong>Unclear or conflicting:</strong> Log the issue and recommend clarification. <em>\"Drawing "
            "M-201 and Spec 23 36 00, 3.2.A conflict on VAV box access clearance. Recommend GC submit RFI to the "
            "EOR for clarification.\"</em>",
            "<strong>Silent:</strong> If no document addresses the condition, it is not a contract deficiency. "
            "Log it as an Observation or Recommendation for the owner and design team.",
            "<strong>Different, but arguably better:</strong> It is still a deviation. Only the owner and EOR can "
            "accept a deviation. Route it to them; do not approve it in the field.",
        ], ordered=False),
    ),
    section(
        h2text("Weak vs. Strong Solutions",
               table(
                   ["Weak (avoid)", "Strong (use)"],
                   [
                       ["\"Fix it.\"",
                        "\"Install the missing strainer per Drawing M-501, Detail 3 and notify CxA for "
                        "re-inspection.\""],
                       ["\"Needs to be redone.\"",
                        "\"Re-terminate sensor wiring per approved submittal 23 09 23-004, p. 12, and provide "
                        "point-to-point checkout record for VAV-2-14.\""],
                       ["\"Move it 2 feet to the left.\" (directing means and methods)",
                        "\"Provide 36 in. minimum working space in front of LP-2A per NEC 110.26(A)(1).\""],
                       ["\"Talk to the engineer.\"",
                        "\"Recommend GC submit RFI to the EOR to resolve the conflict between M-201 and Spec 23 36 "
                        "00, 3.2.A. Issue remains open pending RFI response.\""],
                   ])
               + EXAMPLES_NOTE),
    ),
    section(
        h2text("Define the Closure Criteria",
               "<p>Say up front what evidence will close the issue, so there is no debate later: a re-inspection "
               "photo, a retest of specific functional test steps, a revised submittal, a test report, or a BAS "
               "trend. Match the closure criteria to the issue's priority (see Issue Classification).</p>"),
    ),
)

p_prepared = page(
    "Bring Your References. Don't Rush.",
    section(
        hero(),
        text("<p>Projects are moving at an unprecedented pace. That pace is exactly when shortcuts happen and "
             "credibility is lost. Speed does not excuse an unsupported call. A wrong issue logged in a hurry costs "
             "more time than it saves, and it weakens every issue you write after it.</p>"
             "<p>Get back to the basics: <strong>be prepared before you walk, and be sure before you write.</strong>"
             "</p>"),
    ),
    section(
        h2text("Before the Walk: Pack Your References",
               "<p>Have the documents in your hand, not back at the trailer. Mechanical rooms, basements and "
               "rooftops often have no signal, so download for offline use.</p>"),
        lst([
            "Current spec sections for the systems you are inspecting (including Division 01: 01 40 00 and 01 91 00)",
            "Current drawing sheets, including details, schedules and the latest revisions",
            "Addenda, ASIs, bulletins and RFI responses that affect the area",
            "Approved submittals and manufacturer IOMs for the equipment",
            "The checklists or functional test scripts you will be executing",
            "Open issues for the area and equipment, so you can verify and update them",
            "Charged tablet with offline access, plus camera, flashlight and tape measure",
        ], ordered=False),
    ),
    section(
        h2text("In the Field: Slow Down to Be Right",
               "<p>When you see something that looks wrong, run through this before you raise it:</p>"),
        lst([
            "<strong>Pause.</strong> Do not call it out on the spot just because it looks wrong.",
            "<strong>Find the requirement.</strong> Open the spec or drawing and read the actual paragraph.",
            "<strong>Confirm it is current.</strong> Check the revision, and check for an RFI, ASI or approved "
            "deviation that changed it.",
            "<strong>Verify the condition.</strong> Confirm the tag and location, measure it, and photograph it "
            "(wide and close-up).",
            "<strong>Then write it.</strong> Use the issue formula: location, condition, Not IAW / Contrary to, "
            "required action, evidence.",
        ]),
    ),
    section(
        h2text("\"Let Me Verify That\" Is a Professional Answer",
               "<p>If a contractor asks you to justify something and you do not have the reference in front of "
               "you, do not guess and do not argue. Say:</p>"
               "<p><em>\"Good question. Let me pull up the requirement and I'll follow up with the exact "
               "reference.\"</em></p>"
               "<p>Then follow up. Every time. An issue logged an hour later with the right citation is worth far "
               "more than one logged right away on a hunch.</p>"),
    ),
    section(
        h2text("Field Readiness Checklist",
               "<p>Before every site walk, confirm:</p>"),
        lst([
            "I have the current specs, drawings and revisions for today's scope available offline.",
            "I have the approved submittals and IOMs for the equipment I'm inspecting.",
            "I have checked for RFIs, ASIs and bulletins that affect today's scope.",
            "I have reviewed the open issues for the areas I'm walking.",
            "My tablet is charged, and my platform logins (BIM360, Cx Alloy) work.",
            "I will cite before I call, and I will not rush an issue I cannot support.",
        ], ordered=False, checklist=True),
    ),
)

p_practice = page(
    "Practice: Rewrite the Issue",
    section(
        hero(),
        text("<p>Each scenario below starts with an issue written the way we too often see it in the field. "
             "Before reading the improved version, try rewriting it yourself using the issue formula: "
             "<strong>Location → Condition → Not IAW / Contrary to → Required Action → Evidence</strong>.</p>"
             + EXAMPLES_NOTE),
    ),
    section(
        h2text("Scenario 1: Insulation",
               "<p><strong>As written:</strong> <em>\"Insulation is garbage on AHU-2. Sub needs to redo.\"</em></p>"
               "<p><strong>Rewritten:</strong> <em>\"AHU-2 – Discharge duct insulation incomplete. Level 3 mech room: "
               "approx. 6 ft of supply duct downstream of the AHU-2 discharge plenum is uninsulated. Not IAW Spec "
               "23 07 13, 3.2.A. Required action: Insulate per Spec 23 07 13 and notify CxA for re-inspection. See "
               "Photos 1–2.\"</em></p>"
               "<p><strong>Why it works:</strong> It removes the judgment (\"garbage\"), states the actual condition "
               "and quantity, cites the requirement, and defines closure.</p>"),
    ),
    section(
        h2text("Scenario 2: Tribal Knowledge",
               "<p><strong>As written:</strong> <em>\"We always put a strainer before the control valve. Add "
               "one.\"</em></p>"
               "<p><strong>Rewritten:</strong> <em>\"AHU-1 – Strainer missing upstream of CHW control valve CV-4. "
               "Contrary to Drawing M-501, Detail 3 (Rev 2), which shows a strainer with blow-down valve upstream "
               "of each coil control valve. Required action: Provide strainer per the cited detail. See Photo "
               "3.\"</em></p>"
               "<p><strong>Why it works:</strong> \"We always\" is tribal knowledge. The drawing detail is a "
               "requirement. If the detail did <em>not</em> show a strainer, this would be a Recommendation to the "
               "owner and EOR, not a deficiency.</p>"),
    ),
    section(
        h2text("Scenario 3: The Contractor Pushes Back",
               "<p><strong>Situation:</strong> You log that the flexible duct to VAV-2-14 is 9 ft long. The "
               "mechanical foreman says, \"The engineer told us that was fine.\"</p>"
               "<p><strong>Opinion-based response:</strong> <em>\"Nobody runs flex that long. It's wrong.\"</em></p>"
               "<p><strong>Fact-based response:</strong> <em>\"Spec 23 33 00, 3.5.B limits flex runs to 5 ft. If "
               "there's an RFI response or approved deviation that allows the longer run, send me the number and "
               "I'll reference it and close the issue. Otherwise it stays open as written.\"</em></p>"
               "<p><strong>Why it works:</strong> It points to the document, invites the contractor to bring their "
               "own document, and keeps the conversation about facts. Facts work both ways: if they produce the "
               "RFI, close the issue gracefully and cite it.</p>"),
    ),
    section(
        h2text("Scenario 4: Can't Find the Requirement",
               "<p><strong>Situation:</strong> A sensor is mounted in a spot you believe will give poor readings, "
               "but you cannot find a spec paragraph or detail that addresses its location.</p>"
               "<p><strong>Wrong move:</strong> Logging <em>\"Sensor in wrong location, relocate\"</em> as a "
               "deficiency assigned to the controls contractor.</p>"
               "<p><strong>Right move:</strong> Log a labeled Recommendation: <em>\"Recommendation (not a contract "
               "requirement): Duct static pressure sensor for AHU-3 is located approx. 2 ft downstream of a "
               "fitting, which may produce unstable readings. Owner and EOR to review whether relocation is "
               "desired.\"</em></p>"
               "<p><strong>Why it works:</strong> Your expertise is shared honestly, without presenting an opinion "
               "as a contract requirement.</p>"),
    ),
)

p_summary = page(
    "Summary: Your Field Pocket Guide",
    section(
        hero(),
        text("<p>We need to get back to the basics and always be prepared in the field. Keep these principles "
             "with you on every walk.</p>"),
    ),
    section(
        h2text("The Six Elements of Every Issue", ""),
        lst([
            "<strong>Location</strong>: building, level, room or gridline, and equipment tag",
            "<strong>Condition</strong>: what you observed or measured, objectively, with units",
            "<strong>Citation</strong>: Not IAW / Contrary to the specific section, paragraph, sheet or detail, "
            "with key language quoted",
            "<strong>Evidence</strong>: wide and close-up photos with markups, readings, screenshots",
            "<strong>Solution</strong>: the compliant end condition and how closure will be verified",
            "<strong>Classification</strong>: P0–P3 per Spec 01 40 00, with a realistic due date",
        ]),
    ),
    section(
        h2text("The Rules We Work By", ""),
        lst([
            "Facts, not opinions. If you cannot cite it, it is not a deficiency.",
            "Label opinions honestly as Observations or Recommendations, and route them to the owner and EOR.",
            "Search before you create. Reference related, repeat and duplicate issues by number.",
            "Define what compliance looks like, not how to build it.",
            "When documents are unclear or conflicting, recommend an RFI. Do not fill the gap with opinion.",
            "Bring your references. Don't rush. \"Let me verify that\" is a professional answer.",
            "Facts work both ways. When a contractor shows a document that resolves the issue, cite it and close "
            "it.",
        ], ordered=False),
    ),
    section(
        text("<p><strong>The GC and subs can argue with an opinion. They cannot argue with a fact.</strong></p>"),
    ),
)

# ---------------------------------------------------------------- fixes to existing pages

def sub(old, new, count=1):
    global xml
    assert xml.count(old) == count, (old, xml.count(old))
    xml = xml.replace(old, new)


# Welcome page: describe what the course covers.
sub("<content><![CDATA[<p>Welcome to <span class=\"variable\">{{moduleTitle}}</span>.</p>]]></content>",
    "<content><![CDATA[<p>Welcome to <span class=\"variable\">{{moduleTitle}}</span>.</p>"
    "<p>In this course you will learn to prepare for the field, separate facts from opinions, cite specifications "
    "and drawings precisely, write issues using \"Not IAW\" and \"Contrary to\", create and cross-reference issues, "
    "define clear solutions, and stay factual when the conversation gets heated.</p>"
    "<p><strong>The GC and subs can argue with an opinion. They cannot argue with a fact.</strong></p>]]></content>")

# Typo in the fundamentals list.
sub("<p>List It connects every discipline", "<p>It connects every discipline")

# Placeholder "Heading" H2s left over from the template.
sub("<cmp.heading uid='yGLyLO9Q2h' level=\"2\"><![CDATA[Heading]]>",
    "<cmp.heading uid='yGLyLO9Q2h' level=\"2\"><![CDATA[Required Elements of Every Issue]]>")
sub("<cmp.heading uid='9XR2HupsrX' level=\"2\"><![CDATA[Heading]]>",
    "<cmp.heading uid='9XR2HupsrX' level=\"2\"><![CDATA[Priority Levels and Closure]]>")
sub("<cmp.heading uid='cJ7k2Pap6m' level=\"2\"><![CDATA[Heading]]>",
    "<cmp.heading uid='cJ7k2Pap6m' level=\"2\"><![CDATA[Let the Documents Do the Talking]]>")

# Pre-inspection: add the "bring references" habit to the existing prep list.
sub("guarantees your inspections are perfectly aligned with the latest designs.</p>]]></content><options  /><popup  />"
    "<thumbnail type=\"none\"></thumbnail></item></dataset>",
    "guarantees your inspections are perfectly aligned with the latest designs.</p>]]></content><options  /><popup  />"
    "<thumbnail type=\"none\"></thumbnail></item>"
    "<item><title><![CDATA[Item title]]></title><content><![CDATA[<p><strong>Check for Changes:</strong> Review "
    "addenda, ASIs, bulletins, RFI responses and open issues for the areas you will walk, so you are citing the "
    "current requirement.</p>]]></content><options  /><popup  /><thumbnail type=\"none\"></thumbnail></item>"
    "</dataset>")

# Conflict management page: add a pushback protocol after the existing text.
conflict_extra = section(
    h2text("When a Contractor Pushes Back",
           "<p>Disagreements are normal. Arguments are optional. Keep the conversation on the documents:</p>"),
    lst([
        "<strong>Listen and acknowledge.</strong> Let them make their case without interrupting.",
        "<strong>Open the document together.</strong> Pull up the cited paragraph or detail on your tablet and "
        "read it with them.",
        "<strong>Ask for their reference.</strong> If they believe the work is compliant, ask which document "
        "supports it (RFI response, ASI, approved submittal or deviation).",
        "<strong>Facts work both ways.</strong> If their document supersedes yours, accept it, cite it in the "
        "issue, and close or revise the issue.",
        "<strong>If it is genuinely unclear, stop debating.</strong> Recommend an RFI to the design team and "
        "note it in the issue.",
        "<strong>Escalate through the right channel.</strong> Unresolved disputes go to your Cx lead and the "
        "owner's representative, not into a field argument.",
        "<strong>Document the conversation.</strong> Add a dated comment to the issue summarizing what was "
        "discussed and the next step.",
    ]),
    h3text("Words That Keep It Factual",
           table(
               ["Instead of…", "Say…"],
               [
                   ["\"That's wrong.\"", "\"This doesn't match Spec ___, paragraph ___. Here's the language.\""],
                   ["\"I don't like how that's done.\"", "\"Is there a requirement that covers this? If not, I'll "
                                                         "note it as a recommendation for the owner.\""],
                   ["\"We've always done it this way.\"", "\"The project documents require ___.\""],
                   ["\"You need to fix this now.\"", "\"Per Spec 01 40 00, this is a P1 issue with a 7-day "
                                                     "resolution.\""],
               ])),
)
sub("protects the overall integrity of the project, and builds lasting trust with both clients and contractors.</p>]]>"
    "</cmp.text></cmp.stack></block.grid></section>",
    "protects the overall integrity of the project, and builds lasting trust with both clients and contractors.</p>]]>"
    "</cmp.text></cmp.stack></block.grid></section>" + conflict_extra)

# ---------------------------------------------------------------- insert new pages


def insert_before_page(uid_, content):
    global xml
    marker = f"<page type=\"md\" cmp=\"standard_md\" group=\"CTc3HvvSUE\" retainscroll=\"true\" completionpoint=\"false\" classlist=\"\" labels=\"\"  uid=\"{uid_}\""
    assert xml.count(marker) == 1, uid_
    xml = xml.replace(marker, content + marker)


# Order: ... Platform Workflows, Facts, Citing, Issue Statement, Rigorous Issue Documentation (existing),
# Creating/Cross-referencing, Solution, Classification (existing), Bring References, Conflict (existing),
# Practice, Summary.
insert_before_page("QyObCqXR9B", p_facts + p_cite + p_statement)
insert_before_page("b9zeCru5O0", p_create + p_solution)
insert_before_page("u7pQwkGNBr", p_prepared)

sub("</page><datasets>", "</page>" + p_practice + p_summary + "<datasets>")
sub("</dataset></datasets>", "</dataset>" + "".join(datasets) + "</datasets>")

open(path, "w", encoding="utf-8").write(xml)
print("pages:", xml.count("<page "), "datasets:", xml.count("<dataset "))
