  import logging
from arcgis.gis import GIS
from ipywidgets import IntProgress
from IPython.display import display, Markdown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

l5s = []
l4s = []
l3s = []
l2s = []
l1s = []
lns = []


class Defect:
    def __init__(self, line, grade, code, distance):
        """
        Initializes a Defect object with line number, grade, code, and distance.

        :param line: Line number of the defect.
        :type line: int
        :param grade: Grade of the defect.
        :type grade: str
        :param code: Code of the defect.
        :type code: str
        :param distance: Distance of the defect.
        :type distance: float
        """
        self.line = line
        self.grade = grade
        self.code = code
        self.distance = distance

    def get_line(self):
        """
        Returns the line number of the defect.

        :return: Line number of the defect.
        :rtype: int
        """
        return self.line

    def display_defect(self):
        """
        Displays the defect information using Markdown.

        :return: None
        """
        display(
            Markdown(
                f"<li>Line: {self.line} || Grade: {self.grade} || Code: {self.code} || Distance: {self.distance}</li>"
            )
        )


class Inspection:
    def __init__(
        self,
        segment_id,
        count_level0,
        count_level1,
        count_level2,
        count_level3,
        count_level4,
        count_level5,
    ):
        """
        Initializes an Inspection object with segment ID and defect counts for different levels.

        :param segment_id: ID of the inspection segment.
        :type segment_id: int
        :param count_level0: Count of level 0 defects.
        :type count_level0: int
        :param count_level1: Count of level 1 defects.
        :type count_level1: int
        :param count_level2: Count of level 2 defects.
        :type count_level2: int
        :param count_level3: Count of level 3 defects.
        :type count_level3: int
        :param count_level4: Count of level 4 defects.
        :type count_level4: int
        :param count_level5: Count of level 5 defects.
        :type count_level5: int
        """
        self.segment_id = segment_id
        self.count_level0 = count_level0
        self.count_level1 = count_level1
        self.count_level2 = count_level2
        self.count_level3 = count_level3
        self.count_level4 = count_level4
        self.count_level5 = count_level5
    
    def display_inspection(self):
        """
        Displays the inspection information using Markdown.

        :return: None
        """
        display(
            Markdown(
                f"<li>Line: {self.segment_id} || Level 0: {self.count_level0} Level 1: {self.count_level1} Level 2: {self.count_level2} Level 3: {self.count_level3} Level 4: {self.count_level4} Level 5: {self.count_level5}"
            )
        )


def getGIS():
    logger.info("Connecting to ArcGIS Online Org account...")
    gis = GIS("portal", "user", "password")
    logger.info("Logged in as %s", gis.properties.user.username)
    return gis


def sortDefects(inspection_base, fetch_defects):
    for d in fetch_defects:
        defect_line_to_point = d.attributes["LineToPoint"]
        segment = inspection_base.query(
            where=f"LINETOPOINT = '{defect_line_to_point}'"
        ).features[0]
        segment_id = segment.attributes["SEGMENT_ID"]
        defect = Defect(
            segment_id,
            d.attributes["Grade"],
            d.attributes["PACP_Code"],
            d.attributes["Distance"],
        )
        grade = d.attributes["Grade"]
        if grade == 1:
            l1s.append(defect)
        elif grade == 2:
            l2s.append(defect)
        elif grade == 3:
            l3s.append(defect)
        elif grade == 4:
            l4s.append(defect)
        elif grade == 5:
            l5s.append(defect)
        elif grade is None:
            lns.append(defect)


def get_submission_defects(submission_id):
    """
    Retrieves defects for a given submission ID from ArcGIS Online Org account.

    :param submission_id: ID of the submission.
    :type submission_id: str
    """

    gis = getGIS()
    # Search for Mt_Lebanon_ssMgmtSys_SMSView feature layer
    sms = gis.content.search("title: Mt_Lebanon_ssMgmtSys_SMSView", "Feature Layer")
    
    # Get defect base layer
    logger.info("Getting defect base layer...")
    defect_base = sms[0].layers[0]
    # Get inspections base layer
    inspections_base = sms[0].layers[9]

    # Fetch inspections for the given submission ID
    logger.info("Fetching inspections...")
    fetch_inspections = inspections_base.query(
        where=f"InspectionName='{submission_id}'"
    )

    # Fetch defects for the given submission ID
    logger.info("Fetching defects...")
    fetch_defects = defect_base.query(
        where=f"InspectionName='{submission_id}' and Grade >= 0"
    )
    if (fetch_defects):
        logger.info("Success: Defect Layer Retrieved.")
    else:
        logger.error("Error: Invalid Repair ID.")
        return
        

    # Initialize lists to store defects based on grade
    logger.info("Initializing defect categories...")

    inspections = []
    logger.info("Success: Defect categories initialized.")

    # Categorize defects based on grade
    logger.info("Categorizing defects based on grade...")
    defect_count = len(fetch_defects.features)
    logger.info("Total defects: %s", defect_count)

    sortDefects(inspections_base, fetch_defects)

    logger.info("Success: Categorized all defects by grade.")
    logger.info("See below for data.")

    display(Markdown("<h3>Level 5 Defects</h3>"))
    for d in l5s:
        d.display_defect()

    display(Markdown("<h3>Level 4 Defects</h3>"))
    for d in l4s:
        d.display_defect()

    display(Markdown("<h3>Level 3 Defects</h3>"))
    for d in l3s:
        d.display_defect()


get_submission_defects("43 - O&M 6-9_6-26-20asdf23")
