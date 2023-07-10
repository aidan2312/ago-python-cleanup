import datetime as dt
import logging
from arcgis.gis import GIS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def archive_defects(repair_id, sms_service):
    """
    Archives defects associated with a completed repair in the SMSView feature layer.

    :param repair_id: ID of completed repair.
    :type repair_id: str
    :param sms_service: Title of the SMS Service.
    :type sms_service: str
    :return: None
    """
    logger.info("Starting archive_defects function...")

    # Connect to ArcGIS Online Org account
    logger.info("Connecting to ArcGIS Online Org account...")
    gis = GIS("portal", "user", "password")
    logger.info("Logged in as %s", gis.properties.user.username)

    # Search for the SMS layer
    logger.info("Searching for SMS service...")
    sms = gis.content.search(f"title: {sms_service}", "Feature Layer")

    # Get the defect base layer
    logger.info("Getting the defect base layer...")
    defect_base = sms[0].layers[0]

    # Query for the repair with the specified ID
    logger.info("Querying for the repair with the specified ID...")
    repair_query = sms[0].layers[7].query(where=f"RepairID = '{repair_id}'")

    # Check if the repair with the specified ID exists
    if len(repair_query) == 0:
        logger.error("Invalid Repair ID")
        return "Invalid Repair ID"

    # Check if the repair is complete
    repair_status = repair_query.features[0].attributes["Status"]
    if repair_status != "Complete":
        logger.warning("Repair not complete.")
        return

    # Get the segment ID of the completed repair
    segment_id = repair_query.features[0].attributes["SEGMENT_ID"]

    # Query for previous inspections of the segment
    logger.info("Querying for previous inspections of the segment...")
    prev_inspections = sms[0].layers[9].query(where=f"SEGMENT_ID = '{segment_id}' and STATUS = 're-tv''d'")
    logger.info("Number of inspections impacted: %s", len(prev_inspections))

    # Get defects associated with previous inspections
    logger.info("Getting defects associated with previous inspections...")
    defects = []
    for inspection in prev_inspections.features:
        logger.info("Inspection Name: %s", inspection.attributes["InspectionName"])
        ltp = inspection.attributes["LineToPoint"]
        idefects = defect_base.query(where=f"LineToPoint = '{ltp}'").features
        for defect in idefects:
            defects.append(defect)
            if defect.attributes["Status"] == "re-tv'd":
                logger.info("Defect is already marked Re-TV'd, skipping...")

    # Archive defects
    logger.info("Archiving defects...")
    logger.info("Number of defects impacted: %s", len(defects))
    proceed = input("Proceed? Y/N")
    if proceed.lower() == "y":
        for defect in defects:
            defect.attributes["Status"] = "re-tv'd"
            results = defect_base.edit_features(updates=[defect])
            logger.info("Defect archived: %s", results)
    else:
        logger.info("Operation halted by user.")

# Use the argument below to specify a repair ID e.g. "2023-SNL71", "Pittsburgh_SmsView"
archive_defects("2023-SNL71", "SMS Service Title")
