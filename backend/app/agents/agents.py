from pydantic import BaseModel, Field
from typing import List
from langchain.output_parsers import PydanticOutputParser
from rag_pipeline.qdrant_indexer import QdrantIndexer
from agents.supreme_agent import supreme_agent, supreme_vision_agent, supreme_vision_agent_one_img, supreme_text_agent
from agents.prompts import BASIC_INFO_PROMPT, BASIC_INFO_QUERY, PART_SPECIFIC_BASIC_INFO_PROMPT, PART_SPECIFIC_BASIC_INFO_QUERY, BASIC_INFO_SYSTEM_PROMPT, PART_INFO_SYSTEM_PROMPT, DRAWING_INFO_SYSTEM_PROMPT, KUN_QUOTE_SYSTEM_PROMPT, DATES_PROMPT, MOOG_DOC_PROMPT, MOOG_DOC_QUERY, DRAWING_NOTES_PROMPT
import json
import pandas as pd


def basic_info_agent(qdrant_indexer: QdrantIndexer):
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """
    print("Basic Info Agent")
    class MoogInfo(BaseModel):
        revision: str = Field(description="Revision of the document.")
        visual_inspection: str = Field(description="Visual Inspection along with point number.")
        production_part_approval_process: str = Field(description="Production Part Approval Process.")
        flow_down_requirements: str = Field(description="Flow Down Requirements or flow down specification to sub-tier.")
        prohibited_substances: str = Field(description="The substances/items prohibited from use in processing or manufacturing of parts.")
        statutory_regulatory_requirements: str = Field(description="Statutory and Regulatory Requirements.")

    
    parser = PydanticOutputParser(pydantic_object=MoogInfo)

    query = MOOG_DOC_QUERY
    # Get relevant documents
    relevant_docs = qdrant_indexer.get_relevant_docs(query)
    
    # Join the relevant docs
    context = "\n".join([doc for sublist in relevant_docs for doc in sublist])
    
    # Get response from agent
    response = supreme_agent(MOOG_DOC_PROMPT, context, parser)

    return response

def basic_info_agent_2(image_urls: List[str]):
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """

    response = supreme_vision_agent(image_urls=image_urls, system_prompt=BASIC_INFO_SYSTEM_PROMPT)

    for res in response:
        if res.startswith("```json"):
            # convert to dict
            response = json.loads(res.replace("```json", "").replace("```", ""))


            return response
        
def all_dates_agent(image_url: str):
    """This function is used to interact with the LLM using the langchain library.

    Args:
        image_urls (List[str]): List of image urls.

    Returns:
        dict: The response from the LLM.
    """
    response = supreme_vision_agent_one_img(image_url=image_url, system_prompt=DATES_PROMPT)

    for res in response:
        if res.startswith("```json"):
            # convert to dict
            response = json.loads(res.replace("```json", "").replace("```", ""))

            return response

def part_specific_basic_info_agent(qdrant_indexer: QdrantIndexer):
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """

    class PartSpecs(BaseModel):
        part_number: str = Field(description="Part Number mentioned in the purchase order")
        part_name: str = Field(description="Part name mentioned in the purchase order.")
        part_quantity: int = Field(description="Part Quantity mentioned in the purchase order")
        part_revision_status: str = Field(description="Part Revision Status mentioned in the purchase order. Always check for the latest part revision status in the purchase order.")

    class PartSpecificBasicInfo(BaseModel):
        parts: List[PartSpecs] = Field(description="List of parts mentioned in the purchase order")

    
    parser = PydanticOutputParser(pydantic_object=PartSpecificBasicInfo)

    query = PART_SPECIFIC_BASIC_INFO_QUERY
    # Get relevant documents
    relevant_docs = qdrant_indexer.get_relevant_docs(query)
    
    # Join the relevant docs
    context = "\n".join([doc for sublist in relevant_docs for doc in sublist])
    
    # Get response from agent
    response = supreme_agent(PART_SPECIFIC_BASIC_INFO_PROMPT, context, parser)
    return response

def part_info_agent(image_urls: List[str]):
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """

    response = supreme_vision_agent(image_urls=image_urls, system_prompt=PART_INFO_SYSTEM_PROMPT)

    for res in response:
        if res.startswith("```json"):
            # convert to dict
            response = json.loads(res.replace("```json", "").replace("```", ""))

            print("Response:", response)

            return response
        
def drawing_info_agent(image_urls: List[str]):
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """

    response = supreme_vision_agent(image_urls=image_urls, system_prompt=DRAWING_INFO_SYSTEM_PROMPT)

    for res in response:
        if res.startswith("```json"):
            # convert to dict
            response = json.loads(res.replace("```json", "").replace("```", ""))

            return response
        
def kun_quote_info_agent(image_urls: List[str], po_unit_price: str, po_delivery_date: str):
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """
    formatted_prompt = KUN_QUOTE_SYSTEM_PROMPT.replace("{{po_unit_price}}", po_unit_price).replace("{{po_delivery_date}}", po_delivery_date)

    response = supreme_vision_agent(image_urls=image_urls, system_prompt=formatted_prompt)

    for res in response:
        if res.startswith("```json"):
            # convert to dict
            response = json.loads(res.replace("```json", "").replace("```", ""))

            return response
        
def drawing_notes_agent(drawing_notes: str):
    """This function is used to interact with the LLM using the langchain library.

    Args:
        agent_query (str): The user query.
        context (str): The context for the user query.

    Returns:
        dict: The response from the LLM.
    """
    formatted_prompt = DRAWING_NOTES_PROMPT.replace("{{drawing_notes}}", drawing_notes)

    response = supreme_text_agent(formatted_prompt)


    if response['content'].startswith("```json"):
        response = json.loads(response['content'].replace("```json", "").replace("```", ""))

        return response

def rts_agent(excel_file: str):
    rts_res = {}
    df = pd.read_excel(excel_file)

    rts_mask = df.eq("RTS No.")
    if rts_mask.any().any():
        rts_positions = [(i, j) for i, j in zip(*rts_mask.values.nonzero())]        
        row_idx, col_idx = rts_positions[0]
        if col_idx + 1 < len(df.columns):
            rts_no = df.iat[row_idx, col_idx + 1]
            rts_res["rts_no"] = rts_no
            print("RTS No. found:", rts_no)
        else:
            rts_res["rts_no"] = "RTS No. not found"
            print("No adjacent column to the right for RTS No.")
    else:
        rts_res["rts_no"] = "RTS No. not Specified"
        print("RTS No. not found in DataFrame.")

    rfq_mask = df.eq("RFQ No:")
    rfq_no = "nan"
    if rfq_mask.any().any():
        rfq_positions = [(i, j) for i, j in zip(*rfq_mask.values.nonzero())]
        row_idx, col_idx = rfq_positions[0]        
        if col_idx + 1 < len(df.columns):
            rfq_no = df.iat[row_idx, col_idx + 1]
            if str(rfq_no) == "nan":
                rfq_no = df.iat[row_idx, col_idx + 2]
            rts_res["rfq_no"] = rfq_no
            print("RFQ No. found:", rfq_no)
        else:
            rts_res["rfq_no"] = "RFQ No. not found"
            print("No adjacent column to the right for RFQ No.")
    else:
        rts_res["rfq_no"] = "RFQ No. not Specified"
        print("RFQ No. not found in DataFrame.")

    return rts_res

def quote_ms_excel_agent(excel_file: str, part_number: str, po_date: str, yearly_totals: dict):

    quote_res = {}
    df = pd.read_excel(excel_file)

    header_row_index = df[df.eq("Part Number").any(axis=1)].index[0]

    new_header = df.iloc[header_row_index].tolist()
    df.columns = new_header

    df = df.iloc[header_row_index+1:].reset_index(drop=True)

    df = df[df["Part Number"] == part_number]

    price_column = [col for col in df.columns if "price" in str(col).lower()]

    nre_col = [col for col in df.columns if "nre" in str(col).lower()]

    quote_res["qex_unit_price"] = str(df[price_column].values[0][0])

    quote_res["qex_nre_cost"] = "Not specified" if str(df[nre_col].values[0][0]) == "nan" else str(df[nre_col].values[0][0])

    quote_res["lead_time"] = "Not specified" if "Leadtime" not in df.columns else str(df["Leadtime"].values[0])

    po_year = po_date.split("-")[-1]
    # Extract year columns (convert column names to strings and filter)
    year_columns = [col for col in map(str, df.columns) if col.isdigit() or (col.split('.')[0].isdigit())]

    # Check for exact match
    if int(po_year) in year_columns:
        closest_year = int(po_year)
    else:
        # Find the closest year if exact match is not found
        closest_year = min(year_columns, key=lambda x: abs(int(float(x)) - int(po_year)))

    # Get the value for the found year column
    closest_year_value = df.iloc[0][int(closest_year)]

    print(f"Year: {closest_year}, Value: {closest_year_value}")


    # check if the moq is less than yearly total
    print("Yearly Totals:", yearly_totals[closest_year])

    if int(closest_year_value) < int(yearly_totals[closest_year]):
        quote_res["moq_check"] = "Yes" + f" (Yearly Total: {yearly_totals[closest_year]})" + f" (MOQ: {closest_year_value})"
    else:
        quote_res["moq_check"] = "No" + f" (Yearly Total: {yearly_totals[closest_year]})" + f" (MOQ: {closest_year_value})"


    return quote_res

def kun_asl_excel_agent(excel_file: str):

    df = pd.read_excel(excel_file)

    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)

    result = {}

    for group_name, group_df in df.groupby("Group Name"):
        result[group_name] = group_df[["BP Name", "BP Code", "Active"]].to_dict(orient="records")

    return result

