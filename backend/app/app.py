from fastapi import FastAPI, HTTPException, File, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
import re

# Load environment variables
load_dotenv()

# Add the parent directory to system path to import local modules
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from extractors.pdf_extractor import extract_pdf
from extractors.pdf_images import pdf_pages_to_images, drawing_pdf_to_images
from rag_pipeline.qdrant_indexer import QdrantIndexer
from agents.agents import basic_info_agent, part_specific_basic_info_agent, basic_info_agent_2, part_info_agent, drawing_info_agent, kun_quote_info_agent, rts_agent, quote_ms_excel_agent, all_dates_agent, kun_asl_excel_agent, drawing_notes_agent

# Get credentials from .env
USERNAME = os.getenv("APP_USERNAME")
PASSWORD = os.getenv("APP_PASSWORD")
print(USERNAME, PASSWORD)
if not USERNAME or not PASSWORD:
    raise ValueError("USERNAME and PASSWORD must be set in .env file")

# Global variable to store the indexer
pdfs = None
po_temp_dir = None
drawing_temp_dir = None

# Pydantic model for login
class LoginRequest(BaseModel):
    username: str
    password: str

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
async def login(login_data: LoginRequest):
    print(login_data)
    print(USERNAME, PASSWORD)
    if login_data.username != USERNAME or login_data.password != PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    return {"message": "Login successful"}

@app.post("/upload-pdfs")
async def upload_pdfs(
    moogFiles: Optional[List[UploadFile]] = File(None),
    kunFiles: List[UploadFile] = File(...),
    username: str = Header(..., alias="X-Username"),
    password: str = Header(..., alias="X-Password")
):
    # Verify credentials
    if username != USERNAME or password != PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Create temp directory
    global moog_temp_dir, kun_temp_dir
    moog_temp_dir = tempfile.mkdtemp()
    kun_temp_dir = tempfile.mkdtemp()

    print("kun files:", kunFiles)
    
    # Initialize pdf_paths as list of lists [po_paths, drawing_paths]
    pdf_paths = [[], []]
    try:
        # Process MOOG Files
        if moogFiles:
            for moogFile in moogFiles:
                if not (moogFile.filename.endswith('.pdf') or moogFile.filename.endswith('.xlsx')):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid file format. Only PDF files are supported: {moogFile.filename}"
                    )
                
                safe_moog_filename = f"{moogFile.filename}"
                moog_file_path = Path(moog_temp_dir) / safe_moog_filename

                with moog_file_path.open("wb") as buffer:
                    shutil.copyfileobj(moogFile.file, buffer)
                pdf_paths[0].append(str(moog_file_path))
                print(f"Uploaded MOOG File: {moog_file_path}")

        # Process KUN Files
        for kunFile in kunFiles:
            if not (kunFile.filename.endswith('.pdf') or kunFile.filename.endswith('.xlsx')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file format. Only PDF files are supported: {kunFile.filename}"
                )
            
            safe_kun_filename = f"{kunFile.filename}"
            kun_file_path = Path(kun_temp_dir) / safe_kun_filename

            with kun_file_path.open("wb") as buffer:
                shutil.copyfileobj(kunFile.file, buffer)
            pdf_paths[1].append(str(kun_file_path))
            print(f"Uploaded KUN File: {kun_file_path}")

        # Process PDFs and store indexer globally
        global pdfs
        pdfs = pdf_paths

        print(pdf_paths)

        return {"message": "Files uploaded and processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/process-pdfs")
async def process_pdfs(
    username: str = Header(..., alias="X-Username"),
    password: str = Header(..., alias="X-Password")
):
    # Verify credentials
    if username != USERNAME or password != PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    # documents = extract_pdf(pdfs)
    # qdrant_indexer = QdrantIndexer(documents)
    po_images = []
    drawing_images = []
    kun_quote_images = []
    qex_file_path = None
    print("Processing PDFs")
    print(pdfs)
    print("before======", pdfs[0])

    po_t_n_c = "Not Reviewed"
    for pdf in pdfs[0]:
        if "Terms & Conditions" in pdf:
            pdfs[0].remove(pdf)
            po_t_n_c = "Reviewed"
    print("after======", pdfs[0])

    documents = extract_pdf(pdf_path=pdfs[0])
    qdrant_indexer = QdrantIndexer(documents)




    # Process PO files first, then drawings
    for pdf_list in pdfs[1]:
        print("======", pdf_list.split("/")[-1])
        if pdf_list.split("/")[-1].startswith("RPT") or pdf_list.split("/")[-1].startswith("PO"):
            po_images.extend(pdf_pages_to_images(pdf_list))
        elif "quote" in pdf_list.split("/")[-1].lower() and pdf_list.split("/")[-1].endswith(".pdf"):
            print("Kun Quote PDF")
            kun_quote_images.extend(pdf_pages_to_images(pdf_list))
        elif "drawing" in pdf_list.split("/")[-1].lower() or pdf_list.split("/")[-1].startswith("C"):
            drawing_images.extend(drawing_pdf_to_images(pdf_list))
        elif pdf_list.split("/")[-1].startswith("RTS"):
            print("RTS excel")
            rts_info = rts_agent(pdf_list)
            print("RTS Info:", rts_info)
        elif pdf_list.split("/")[-1].startswith("Quote") and pdf_list.split("/")[-1].endswith(".xlsx"):
            print("Kun Quote excel")
            qex_file_path = pdf_list
        elif "asl" in pdf_list.split("/")[-1].lower() and pdf_list.split("/")[-1].endswith(".xlsx"):
            print("ASL excel")
            asl_output = kun_asl_excel_agent(pdf_list)
            print("ASL Images:", asl_output)
            

    # Check if indexer exists
    if qdrant_indexer is None:
        raise HTTPException(
            status_code=400,
            detail="No PDFs have been uploaded yet"
        )
    print("Processing PDFs")
    try:
        moog_doc_response = basic_info_agent(qdrant_indexer)
        print("MOOG Doc Response:", moog_doc_response)

        basic_info = basic_info_agent_2(po_images)
        print("Basic Info:", basic_info)

        dates_info = all_dates_agent(po_images[0])
        print("Dates Info:", dates_info)

        parts_info = part_info_agent(po_images)
        print("Parts Info:", parts_info)

        drawing_info = drawing_info_agent(drawing_images)
        print("draw Info:", drawing_info)



        today_date = datetime.now().strftime("%d-%m-%Y")

        basic_info_response = {
            "project": basic_info["project"],
            "po_number": basic_info["po_number"],
            "po_date": basic_info["po_date"],
            "vendor_number": basic_info["vendor_no"],
            "vendor_terms": basic_info["vendor_terms"],
            "contract_review_raise_date": today_date,
            "ex_works": basic_info["exw"],
            "nre_cost": basic_info["nre_cost"],
            "moog_supplier_quality_requirements": basic_info["moog_supplier_quality_requirements"],


        }

        print("Basic Info Response:", basic_info_response)  

        # Initialize check_info dict
        check_info = {}

        check_info["customer_special_rm_requirements"] = basic_info["customer_special_rm_requirements"]

        # Extract material and revision info from drawings
        quality_material = drawing_info["material"]
        print("Quality Material:", quality_material)
        print("Drawing Info:", drawing_info['revision'])
        draw_latest_revision = max(drawing_info['revision'], key=lambda x: x['date'])
        print("Drawing Latest Revision:", draw_latest_revision)
        print("Drawing Latest Revision:", draw_latest_revision['rev'])

        # Split text on the numbering pattern (e.g., "1.", "2.", etc.)
        formatted_notes = re.split(r'(\d+\.)', drawing_info["notes"])

        # Join each split part to format it properly
        structured_notes = "\n".join([formatted_notes[i] + formatted_notes[i + 1].strip() for i in range(1, len(formatted_notes), 2)])

        check_info["drawing_notes"] = structured_notes

        drawing_notes_info = drawing_notes_agent(check_info["drawing_notes"])
        print("Drawing Notes Info:", drawing_notes_info)

        check_info["drawing_raw_materials"] = drawing_notes_info["raw_material"]
        check_info["drawing_special_process"] = drawing_notes_info["special_process"]
        check_info["drawing_child_part"] = drawing_notes_info["child_part"]
        check_info["drawing_marking"] = drawing_notes_info["marking"]

        formatted_notes_in_triangle = re.split(r'(\d+\.)', drawing_info["notes_in_triangle"])

        structured_notes_in_triangle = "\n".join([formatted_notes_in_triangle[i] + formatted_notes_in_triangle[i + 1].strip() for i in range(1, len(formatted_notes_in_triangle), 2)])

        check_info["critical_characteristics"] = structured_notes_in_triangle

        check_info["material_supplier"] = drawing_info["supplier"]

        check_info["proprietary_info"] = drawing_info["proprietary_info"]

        check_info["red_line_notes"] = drawing_info["red_line_notes"]

        print("Parts Info:", parts_info)

        for part in parts_info:
            po_draw_rev_match = "Not specified"
            if draw_latest_revision['rev'] == part["part_revision_status"]:
                print("Drawing and PO revision match")
                po_draw_rev_match = "Yes" + " " + "'"+draw_latest_revision['rev']+ "'"
            else:
                print("Drawing and PO revision do not match")
                po_draw_rev_match = "No" + " " + "Drawing Rev:" +draw_latest_revision['rev'] + " " + "PO Rev:" + part["part_revision_status"]
            
            basic_info_response["part_number"] = part["part_number"]
            basic_info_response["part_name"] = part["part_name"]
            basic_info_response["part_quantity"] = part["part_quantity"]
            basic_info_response["part_unit_price"] = part["part_unit_price"]
            basic_info_response["part_revision_status"] = part["part_revision_status"]
            basic_info_response["part_po_type"] = part["part_po_type"]
            basic_info_response["date_required"] = part["date_required"]
            basic_info_response["part_quantities"] = part["part_quantities"]

            check_info["special_rm_requirements"] = part["special_rm_requirements"]

            check_info["available_rm_standards"] = quality_material
            check_info["special_quality_requirements"] = part["special_quality_requirements"]
            check_info["po_draw_rev_match"] = po_draw_rev_match
            check_info["quality_clauses"] = part["quality_clauses"]

        print("Basic Info Response:", basic_info_response)
        print("Check Info:", check_info)

        check_info["moog_doc_revision"] = moog_doc_response["revision"]
        check_info["moog_visual_inspection"] = moog_doc_response["visual_inspection"]
        check_info["ppap"] = moog_doc_response["production_part_approval_process"]
        check_info["moog_flow_down_requirements"] = moog_doc_response["flow_down_requirements"]
        check_info["prohibited_substances"] = moog_doc_response["prohibited_substances"]
        check_info["statutory_regulatory_requirements"] = moog_doc_response["statutory_regulatory_requirements"]

        check_info["po_terms_conditions"] = po_t_n_c

        yearly_totals = {}

        # Iterate through the dictionary
        for date, quantity in basic_info_response["part_quantities"].items():
            # Extract the year from the date (first 4 characters)
            year = date[:4]
            
            # Convert the quantity to an integer and add to the year's total
            yearly_totals[year] = yearly_totals.get(year, 0) + int(quantity)

        # Print the results
        for year, total in yearly_totals.items():
            print(f"Year {year}: Total Quantity = {total}")

        if qex_file_path:
            qex_info = quote_ms_excel_agent(qex_file_path, basic_info_response["part_number"], basic_info_response["po_date"], yearly_totals)
            print("QEX Info:", qex_info)
        else:
            qex_info = {
                "qex_unit_price": "Not specified",
                "unit_price_match": "Not specified",
                "qex_nre_cost": "Not specified",
                "lead_time": "Not specified",
                "moq_check": "Not specified",
            }
        print("QEX Info:", qex_info)
        lead_time = 0
        # calculate the weeks between the two dates
        if basic_info_response["date_required"] != "Not specified" and basic_info_response["po_date"] != "Not specified":
            date_required = datetime.strptime(basic_info_response["date_required"], "%d-%m-%Y")
            po_date = datetime.strptime(basic_info_response["po_date"], "%d-%m-%Y")
            lead_time = (date_required - po_date).days // 7
            print("Lead Time:", lead_time)
        qex_lead_time_lower_limit = 0
        qex_lead_time_upper_limit = 0
        if qex_info["lead_time"] != "Not specified":
            # if str(qex_info["lead_time"]) is "28-32" then split it and convert to int
            if "-" in str(qex_info["lead_time"]):
                qex_lead_time_lower_limit = int(qex_info["lead_time"].split("-")[0])
                qex_lead_time_upper_limit = int(qex_info["lead_time"].split("-")[1])
            if lead_time >= qex_lead_time_lower_limit and lead_time <= qex_lead_time_upper_limit:
                qex_info["qex_lead_time_match"] = "Yes" + " " + "PO Lead Time: " + str(lead_time) + " " + "weeks QEX Lead Time: " + str(qex_info["lead_time"] + " weeks")
            else:
                qex_info["qex_lead_time_match"] = "No" + " " + "PO Lead Time: " + str(lead_time) + " " + " weeks QEX Lead Time: " + str(qex_info["lead_time"] + " weeks")

        po_unit_price = round(float(basic_info_response["part_unit_price"]), 2) if basic_info_response["part_unit_price"] != "Not specified" else "Not specified"
        qex_unit_price = round(float(qex_info["qex_unit_price"]), 2) if qex_info["qex_unit_price"] != "Not specified" else "Not specified"

        if po_unit_price != "Not specified" and qex_unit_price != "Not specified":
            if po_unit_price == qex_unit_price:
                qex_info["unit_price_match"] = f"Yes PO Unit Price: {po_unit_price} QEX Unit Price: {qex_unit_price}"
            else:
                qex_info["unit_price_match"] = f"No PO Unit Price: {po_unit_price} QEX Unit Price: {qex_unit_price}"

        if basic_info_response["nre_cost"] == qex_info["qex_nre_cost"]:
            qex_info["nre_cost_match"] = "Yes" + " " + "PO NRE Cost: " + basic_info_response["nre_cost"] + " " + "QEX NRE Cost: " + qex_info["qex_nre_cost"]
        else:
            qex_info["nre_cost_match"] = "No" + " " + "PO NRE Cost: " + basic_info_response["nre_cost"] + " " + "QEX NRE Cost: " + qex_info["qex_nre_cost"]

        kun_quote_info = kun_quote_info_agent(kun_quote_images, po_unit_price=basic_info_response["part_unit_price"], po_delivery_date=basic_info_response["date_required"])
        print("Kun Quote Info:", kun_quote_info)

        for part in kun_quote_info:
            check_info["kun_quotation_date"] = part["quotation_date"]
            check_info["po_date_in_quote"] = part["po_date_in_quote"]

            if part["ex_works"]:
                check_info["ex_works"] = "Ex-works in PO: " + basic_info_response['ex_works'] + ", Ex-works in Quote pdf is " + part["ex_works"]

        print("Today's Date:", today_date)
        print("PO Draw Rev Match:", po_temp_dir)
        # Clean up temp directories
        if po_temp_dir and os.path.exists(po_temp_dir):
            shutil.rmtree(po_temp_dir)
        if drawing_temp_dir and os.path.exists(drawing_temp_dir):
            shutil.rmtree(drawing_temp_dir)
        print("Temp directory removed")

        # Add QEX info to check_info
        check_info.update(qex_info)

        # Add RTS info if exists
        if 'rts_info' in locals():
            check_info.update(rts_info)

        if 'asl_output' in locals():
            if "SPECIAL PROCESS" in asl_output:
                output = "\n".join([f"{i+1}. " + ", ".join(f"{key}: {value}" for key, value in dict_item.items()) for i, dict_item in enumerate(asl_output['SPECIAL PROCESS'])])
                check_info["special_process"] = output
            if "RAW MATERIALS" in asl_output:
                output = "\n".join([f"{i+1}. " + ", ".join(f"{key}: {value}" for key, value in dict_item.items()) for i, dict_item in enumerate(asl_output['RAW MATERIALS'])])
                check_info["asl_raw_materials"] = output

        final_response = {
            "basic_info": basic_info_response,
            "check_info": check_info
        }


        return final_response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)