BASIC_INFO_PROMPT = "Extract the basic information from the given purchase order markdown. Specifically, extract the project or client or customer name mentioned in the purchase order, purchase order number be sure to get only the Purchase order number do not include vendor number, vendor number and purchase order date."

BASIC_INFO_QUERY = "What is the project name, purchase order number, and purchase order date mentioned in the purchase order?"

PART_SPECIFIC_BASIC_INFO_PROMPT = "Extract the part specific basic information from the given purchase order markdown. Specifically, extract the part number, part name, part quantity, and part revision status mentioned in the purchase order. The part name or example BUSHING, BEARING, etc. Most of the time the part name is mentioned in the purchase order as BSHG for BUSHING, BRG for BEARING, etc. The part revision status is mentioned as REV A, REV B, etc. So in for example if there are two revisions like REV: A, REV: B or REV of the part then the latest revision status should be extracted which is REV B. Always check for the latest part revision status in the purchase order."

PART_SPECIFIC_BASIC_INFO_QUERY = "What are the part number, part name, part quantity, and part revision status mentioned in the purchase order?"

BASIC_INFO_SYSTEM_PROMPT = """Extract all the information from the given purchase order. 

Step 1:
Specifically, extract the 
1. Project or Client or Customer name mentioned in the purchase order
2. Purchase order number, be sure to get only the Purchase order number do not include vendor number. Example Purchase order numbers for your reference: FA2410TT04, FA2410Z606, FA2410TT06, FA2303ZP01 etc.
3. Purchase order date: Search the document for an 8-digit number in the format YYYYMMDD. Ensure this is the "PURCH. ORD. DATE" and not any other date. Most of the times it appears after the Purchase order number.  
If it is mentioned as "20241014" get is as "14-10-2024".
4. Vendor terms mentioned in the purchase order. The vendor terms are always mentioned after the text "VENDOR TERMS".
5. Vendor number mentioned in the purchase order. The vendor number is always mentioned after the text "VENDOR NO.".
6. NRE cost: If there is any mention of NRE cost, then extract the NRE cost.
7. EXW: If there is any mention of EXW, then the extracted text should be just EXW, make sure you dont include any other fileds like named place. So the output should be either EXW or Not specified.
8. Moog Supplier Quality Requirements: From the given purchase order document, extract only the 'Moog Special Quality Requirements' (SQR) explicitly stated under the 'SUPPLEMENTAL PURCHASE ORDER REQUIREMENTS' section. Focus on terms like SQR-1, SQR-2, or any other similar special quality requirement codes explicitly labeled as SQR. Ignore other special processes or unrelated text such as REV numbers or standard inspection requirements.
9. If there are any special requirements from customer regarding raw material such as REACh, RoHs, DFARS, Conflict mineral, etc. specified in PO, then extract the special requirements regarding raw material from the purchase order. If there is no mention of special requirements regarding raw material, then output "Not specified".

Step 2:
Format the output in JSON format given below: 
'{{"project": "XXXXX", "po_number": "FA2410TT04", "po_date": "DD-MM-YYYY", "vendor_terms": "90", "vendor_no": "24737", "nre_cost": "XXXXXX", "exw":"EXW / Not specified", "moog_supplier_quality_requirements": "XXXXX", "customer_special_rm_requirements": "XXXXX"}}'.


Step 3:
Make sure you follow all the above steps and extract the information correctly. 
Be careful while extracting the Alphanumeric strings. 
Always format the output in JSON format and format the date.

"""

DATES_PROMPT = """Extract all the dates from the given document. Make sure you extract the dates correctly. If anything is not mentioned in the document, then just output "Not specified".

1. PURCHASE ORDER DATE
If it is mentioned as "20241014" get is as "14-10-2024".

2. DATE REQUIRED
Identify the line or row where the item number, quantity, and part number are mentioned. In that context, find and extract the date in the format YYYYMMDD, which is often labeled as 'DATE REQUIRED' or associated with delivery or scheduling information. And format the date in DD-MM-YYYY. The date required is always the fourth text after the part number.
If it is mentioned as "20250702" get is as "02-07-2025".

3. Difference in weeks between the Purchase Order Date and Date Required.

Format the output in JSON format given below:
'{{"po_date": "DD-MM-YYYY", "date_required": "DD-MM-YYYY", "weeks_diff": "XX"}}'.
"""



PART_INFO_SYSTEM_PROMPT = """Extract all the information about the part from the given purchase order. 
Never hallucinate the information. If anything is not mentioned in the purchase order, then just output "Not specified".

Step 1:
Specifically, extract the 

1. Part Number 
2. Part Name : The part name or example BUSHING, BEARING, etc. Most of the time the part name is mentioned in the purchase order as BSHG for BUSHING, BRG for BEARING, etc. Always change the part name to the full name. For example, if the part name is BSHG, then the part name should be BUSHING.
3. Part Quantity
4. Part Unit Price: Always look under the heading "Unit Price" and extract the unit price.
5. Part Revision Status (Print rev) : The part revision status will be mentioned as A, B, C etc.
6. DATE REQUIRED
Identify the line or row where the item number, quantity, and part number are mentioned. In that context, find and extract the date in the format YYYYMMDD, which is often labeled as 'DATE REQUIRED' or associated with delivery or scheduling information. And format the date in DD-MM-YYYY. The date required is always the fourth text after the part number.
If it is mentioned as "20250702" get is as "02-07-2025".
7. Part Purchase Order Type (PO Type): If there is any mention like for example First Artical Inspection, etc, then the PO Type should be extracted as First Artical Inspection.
8. Special Quality Requirements: For example, S317, S504 & S292,MRQ52620*.
9. Special Requirements Regarding Raw Material: Any special requirement from Customer regarding Raw material for example,  DFARS, REACh, RoHS, Conflict minerals, etc.
10. QUALITY REQUIREMENT CLAUSE(S): If there is any mention of Quality Requirement Clause, then extract the Quality Requirement Clauses along with their revision status. For example, QLTY-1000011 REV: A, S504 REV: -, S317 REV: B, S110 REV: A, S292 REV:T, S292 REV: R etc.
11. Extract all dates in the format YYYYMMDD and their corresponding quantities (numbers) listed next to them in the text. Ensure each date is mapped to its respective quantity. For example, if the text mentions 20250702 5, the output should clearly state: 20250702: 5. Ignore unrelated text.

If there are multiple parts in the purchase order, then extract the information for all the parts as a list.

Step 2:
Format the output in JSON format given below: 
'[{{"part_number": "XXXXX", "part_name": "XXXXX", "part_quantity": "XXXXX", "part_unit_price": "XXXXXX" "part_revision_status": "XXXXX", "part_po_type": "XXXXX", 'date_required': "DD-MM-YYYY" "special_quality_requirements": "XXXXX", "special_rm_requirements": "XXXXX" "quality_clauses": "XXXX REV-X", "part_quantities": ["YYYYMMDD": "X", "YYYYMMDD": "XXX", "YYYYMMDD": "XXX", "YYYYMMDD": "XXX"]}}]'.

Step 3:
Check the output list, if mutiple dictionaries belongs to the same part then merge the dictionaries into a list of single dictionary.

Step 4:
Make sure you follow the above steps and extract the information correctly. Always format the output in JSON format and format the date.
"""

DRAWING_INFO_SYSTEM_PROMPT = """You are an expert in extracting all the information about the drawing from the given drawing images. 
The drawing image is split into 4 equal half and you will be given two images at a time.
Make sure you extract the information correctly.
If anything is not mentioned in the drawing, then just output "Not specified". 

Specifically, extract the

1. Extract the REVISIONS table with the heading "REVISIONS" which have subheadings "ZONE", "REV", "DESCRIPTION", "DATE" and "APPROVED" . Extract all the revisions of the drawing. The revision is always a single alphabet like A, B, C, D, etc. The revision date is mentioned in the format YYYYMMDD, which should be formatted as DD-MM-YYYY. The approved person is always mentioned as XXX/XX or XX/XX.

2. The material of the part which will be given in the table located at the botton right corner with heading MATERIAL. It can also be mentioned in the NOTES section with subheading "MATERIAL". In context you have to identify AMS spec, ASTM spec, AS spec, ANSI Spec, ASME spec. Examples for your reference how material is mentioned in the image: AMS-QQ-S-763, ASTM A666, ASTM A582, ASTM E1417, ASTM A967, AS33514-08, AMS 2451/9, AMS 2417, ANSI Y14.36 & B 46.1, ASME Y14.5M -1994, etc.
    2.1. If there is any mention about the material supplier, then extract the material supplier name otherwise output "Not specified".

3. Extract all the NOTES section from the drawing. 
    3.1 After extracting the notes section, extract the critical notes whose ponit number is placed inside a traingle in the image. For example if the points 1, 4, 5, 6 are inside a triangle then extract the critical notes as "1. XXXXXXXXXXXXX, 4. XXXXXXXXXXX, 5. XXXXXXXXXXX, 6. XXXXXXXXXXX".
    3.2 If there any points underlined with red color, then extract those points as "1. XXXXXXXXXXXXX, 2. XXXXXXXXXXX, 3. XXXXXXXXXXX, 4. XXXXXXXXXXX". Esle output "Not specified".

4. Extract all the Moog Proprietary and Confidential Information from the drawing. The Moog Proprietary and Confidential Information is always mentioned in the box with the heading "MOOG PROPRIETARY AND CONFIDENTIAL INFORMATION". Extract all the information from the box and the box below it.

Always format the output in JSON format and format the date. 

Output format:
 '{{"material": "XXXXX, XXXXXX, XXXXXX, XXXXXX", "supplier": "XXXXX/ Not specified", "revision": [{{"rev": "X", "date": "DD-MM-YYYY"}}, {{"rev": "X", "date": "DD-MM-YYYY"}}, {{"rev": "X", "date": "DD-MM-YYYY"}}, {{"rev": "X", "date": "DD-MM-YYYY"}}], "notes": "1. XXXXXXXXXXXXX, 2. XXXXXXXXXXX, 3. XXXXXXXXXXX, 4. XXXXXXXXXXX", "notes_in_triangle": "1. XXXXXXXXXXXXX, 4. XXXXXXXXXXX, 5. XXXXXXXXXXX, 6. XXXXXXXXXXX", "red_line_notes" : "1. XXXXXXXXXXXXX, 2. XXXXXXXXXXX, 3. XXXXXXXXXXX, 4. XXXXXXXXXXX", "proprietary_info": "XXXXX"}}'.
 """

KUN_QUOTE_SYSTEM_PROMPT = """
You are an expert in extracting information from the given Quotation. You have expertise in comparing and analysing the information with the given quotation and purchase order information. Make sure you follow all steps in getting the information correctly.

Step 1: Extraction.
Extract 
1. The Quotation Date.
2. Notes
    2.1 Ex Works: just check if it is mentioned or not. If mentioned then extract the Ex-works point.
3. Terms and Conditions

Step 2: Comparison.
PO Information:
PO Date: {{po_date}}
Check if PO Date is within the quotation date. If yes, then the output should be "Yes" else "No".

Step 3: Output Format.
After the Step 3 comparison, format the output as  
'[{{"quotation_date": "DD-MM-YYYY", "po_date_in_quote": "Yes/No", "ex_works": "XXXXXXX XXXXXX XXXXXX"}}]'.

Step 4: Final Output.
Get the final output only after following all the steps correctly.
The output should in JSON format, with the keys as mentioned in Step 3.
"""
MOOG_DOC_QUERY = "Extract the revision of the whole document, visual inspection requirement, PPAP requirements, flow down requirements, statutory regulatory requirements and prohibited substances mentioned in the supplier quality and management system requirements document."

MOOG_DOC_PROMPT = """You are an expert in extracting information from the given supplier quality and management system requirements document markdown text.

Extract the 
1. Revision of the whole document. 
2. Visual inspection: Get the point number and the text that tells about visual inspection requirement that parts shall be visually inspected for.
3. Production Part Approval Process: Any mention about PPAP requirements and its level along with its index.
4. Flow down requirements mentioned in the supplier quality and management system requirements document.
5. Prohibited substances: The substances/items (Glass beads, Mercury contamination) prohibited from use in processing or manufacturing of parts mentioned in the supplier quality and management system requirements document.
6. Statutory and Regulatory Requirements: Extract any mention of statutory and regulatory requirements in the document.

Always format the output in JSON format.

Output format:
'{{"revision": "XXXXX", "visual_inspection": "XXXXX", "production_part_approval_process": "XXXXX", "flow_down_requirements": "XXXXX", "prohibited_substances": "XXXXXXX", "statutory_regulatory_requirements": "XXXXX"}}'.
"""

DRAWING_NOTES_PROMPT = """You are tasked with analyzing aerospace drawing notes to extract key information. The notes describe the requirements for a part. Your objective is to identify and classify specific details from the notes.

Drawing notes:
{{drawing_notes}}

Questions to answer:
1. **Raw Material Requirements**: Identify if raw material requirements are specified. If yes, state the requirements. If not, mention "Not specified."
2. **Special Process Requirements**: Identify if any special process requirements are specified (e.g., plating, heat treatment, inspection). If yes, list the requirements. If not, mention "Not specified."
3. **Child Part Requirements**: Identify if there are any references to child parts or sub-component requirements. If yes, specify the requirements. If not, mention "Not specified."
4. **Marking Requirements**: Identify if marking (e.g., engraving, labeling) requirements are specified. If yes, detail the requirements. If not, mention "Not specified."

**Instructions**:
- Provide a clear and concise response for each question.
- Ensure technical terminology is accurate and follows aerospace standards.
- Conclude whether each requirement is specified or not.
- Always format the output in JSON format.

**Output Format**:
'{{"raw_material": "XXXXX", "special_process": "XXXXX", "child_part": "XXXXX", "marking": "XXXXX"}}'.

"""