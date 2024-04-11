import io
import pymongo
from pymongo.errors import DuplicateKeyError
from pymongo.errors import WriteError
from pprint import pprint
from Utilities import Utilities
from bson.objectid import ObjectId


def check_unique(collection, new_document, column_list) -> bool:
    """
    Validate a document to see whether it duplicates any existing documents already in the collection.
    :param collection:      Reference to the collection that we are about to insert into.
    :param new_document:    The Python dictionary with the data for the new document.
    :param column_list:     The list of columns from the index that we're checking.
    :return:                True if this insert should work wrt to this index, False otherwise.
    """
    find = {}  # initialize the selection criteria.
    # build the search "string" that we'll be searching on.
    # Each element in column_list is a tuple: the column name and whether the column is sorted in ascending
    # or descending order.  I don't care about the direction, just the name of the column.
    for column_name, direction in column_list:
        if column_name in new_document.keys():
            # add the next criteria to the find.  Defaults to a conjunction, which is perfect for this application.
            find[column_name] = new_document[column_name]
    if find:
        # count the number of documents that duplicate this one across the supplied columns.
        return collection.count_documents(find) == 0
    else:
        # All the columns in the index are null in the new document.
        return False


def check_all_unique(collection, new_document):
    """
    Driver for check_unique.  check_unique just looks at one uniqueness constraint for the given collection.
    check_all_unique looks at each uniqueness constraint for the collection by calling check_unique.
    :param collection:
    :param new_document:
    :return:
    """
    # get the index metadata from MongoDB on the sections collection
    collection_ind = collection.index_information()  # Get all the index information
    # Cycle through the indexes one by one.  The variable "index" is just the index name.
    for index in collection_ind:
        if index != '_id_':                 # Skip this one since we cannot control it (usually)
            # Get the list of columns in this index.  The index variable is just the name.
            columns = collection_ind[index]
            if columns['unique']:           # make sure this is a uniqueness constraint
                print(
                    f"Unique index: {index} will be respected: {check_unique(sections, new_document, columns['key'])}")


def print_exception(thrown_exception: Exception):
    """
    Analyze the supplied selection and return a text string that captures what violations of the
    schema & any uniqueness constraints that caused the input exception.
    :param thrown_exception:    The exception that MongoDB threw.
    :return:                    The formatted text describing the issue(s) in the exception.
    """
    # Use StringIO as a buffer to accumulate the output.
    with io.StringIO() as output:
        output.write('***************** Start of Exception print *****************\n')
        # DuplicateKeyError is a subtype of WriteError.  So I have to check for DuplicateKeyError first, and then
        # NOT check for WriteError to get this to work properly.
        if isinstance(thrown_exception, DuplicateKeyError):
            error_message = thrown_exception.details
            # There may be multiple columns in the uniqueness constraint.
            # I'm not sure what happens if there are multiple uniqueness constraints violated at the same insert.
            fields = []
            output.write("Uniqueness constraint violated on the fields:")
            # Get the list of fields in the uniqueness constraint.
            for field in iter(error_message['keyValue']):
                fields.append(field)
            output.write(f"{', '.join(fields)}' should be unique.")
        elif isinstance(thrown_exception, WriteError):
            error_message = thrown_exception.details["errInfo"]["details"]
            # In case there are multiple criteria violated at the same time.
            for error in error_message["schemaRulesNotSatisfied"]:
                # One field could have multiple constraints violated.
                field_errors = error.get("propertiesNotSatisfied")
                if field_errors:
                    for field_error in field_errors:
                        field = field_error["propertyName"]
                        reasons = field_error.get("details", [])
                        for reason in reasons:
                            operator_name = reason.get("operatorName")
                            if operator_name == "enum":
                                allowed_values = reason["specifiedAs"]["enum"]
                                output.write(
                                    f"Error: Invalid value for field '{field}'. Allowed values are: {allowed_values}\n")
                            elif operator_name in ["maxLength", "minLength"]:
                                specified_length = reason["specifiedAs"][operator_name]
                                output.write(
                                    f"Error: Invalid length for field '{field}'. The length should be {operator_name} "
                                    f"{specified_length}.\n")
                            elif operator_name == "unique":
                                output.write(
                                    f"Error: field '{field}' already exists. Please choose a different value.\n")
                            elif operator_name == "combineUnique":
                                fields = reason["specifiedAs"]["fields"]
                                output.write(f"Error: Combination of fields '{', '.join(fields)}' should be unique.\n")
                            else:
                                output.write(
                                    f"Error: '{reason['reason']}' for field '{field}'. Please correct the input.\n")
        results = output.getvalue().rstrip()
    return results


def test_try(collection, document, message: str):
    """
    Utility function to insert the given document into the collection and print out the exception under
    a custom message to help ID which results come from which test.
    :param collection:      Pointer to the collection that we're inserting into.
    :param document:        The document that we're inserting.
    :param message:         The banner to print before printing any error messages.
    :return:                None.
    """
    test_section["_id"] = ObjectId()  # Force a new _id value.  I was getting duplicate _id values before.
    print(message)
    try:
        pprint(collection.insert_one(document))
    except Exception as exception:
        print(print_exception(exception))


if __name__ == '__main__':
    """Validator and uniqueness constraints for a Section collection"""
    print("In the Mongo Test Section")
    # create connection to the database.
    db = Utilities.startup()
    sections = db["sections"]
    sections_validator = {
        'validator': {
            '$jsonSchema': {
                'bsonType': "object",
                'description': "An offering of a course.",
                'required': ["department_abbreviation", "course_number", "section_number", "semester", "year",
                             "building", "room", "start_hour", "start_minute", "schedule"],
                'additionalProperties': False,
                'properties': {
                    '_id': {},
                    'department_abbreviation': {
                        'bsonType': "string",
                        'minLength': 3,
                        'maxLength': 10,
                        "description": "The name of the department."
                    },
                    'course_number': {
                        'bsonType': "int",
                        'minimum': 100,
                        'maximum': 499,
                        "description": "A 3-digit number designating a specific course within a department."
                    },
                    'section_number': {
                        'bsonType': "int",
                        "description": "A 2-digit number designating a section offered of a course during a semester."
                    },
                    'semester': {
                        'enum': ["Fall", "Spring", "Summer I", "Summer II", "Winter"],
                        'description': "Time of year for the section to be offered."
                    },
                    'year': {
                        'bsonType': "int",
                        "description": "A 4-digit number designating the year that the section is offered.",
                        "minimum": 1949
                    },
                    'building': {
                        'bsonType': "string",
                        "description": "A string name of the building where the section will meet",
                        "minLength": 3,
                        "maxLength": 10
                    },
                    'room': {
                        'bsonType': "int",
                        "description": "A 3-digit number designating the room where the section will meet.",
                        "minimum": 100,
                        "maximum": 9999
                    },
                    # It is impossible in MongoDB to separate time from date.  In this case, we want to keep it
                    # simple and just track the start hour & minutes, and not even allow all possible minutes.
                    'start_hour': {
                        'bsonType': "int",
                        "description": "The hour when the section starts.",
                        "minimum": 8,
                        "maximum": 18
                    },
                    # We never start a section on the quarter or three quarter hour.
                    'start_minute': {
                        'bsonType': "int",
                        'description': "The minutes into the start_hour when the section starts.",
                        'enum': [0, 30],
                    },
                    # A better way perhaps would be to set up an array of the days of the week when it meets,
                    # but this is far simpler.
                    'schedule': {
                        'bsonType': "string",
                        'description': "The days of the week when the section occurs.",
                        'enum': ["MWF", 'MW', 'TuTh', 'F', 'S']
                    },
                }
            }
        }
    }
    if "sections" in db.list_collection_names():
        print("dropping the sections collection.")
        sections.drop()
    print(db.create_collection("sections", **sections_validator))
    test_section = {
        "department_abbreviation": 'CECS',
        "course_number": 323,
        "section_number": 1,
        "semester": 'Fall',
        "year": 2023,
        "building": 'VEC',
        "room": 331,
        "start_hour": 8,
        "start_minute": 0,
        "schedule": 'MW'
    }
    sections.insert_one(test_section)
    # We cannot have two sections of the same course in the same semester and year and section number.
    sections.create_index([("department_abbreviation", pymongo.ASCENDING), ("course_number", pymongo.ASCENDING),
                           ("section_number", pymongo.ASCENDING), ("semester", pymongo.ASCENDING),
                           ("year", pymongo.ASCENDING)], unique=True, name='sections_uk_01')
    # We cannot have two sections meeting at the same time in the same place.
    sections.create_index([("semester", pymongo.ASCENDING), ("year", pymongo.ASCENDING),
                           ("building", pymongo.ASCENDING), ("room", pymongo.ASCENDING),
                           ("start_hour", pymongo.ASCENDING), ("start_minute", pymongo.ASCENDING),
                           ("schedule", pymongo.ASCENDING)], unique=True, name='sections_uk_02')
    check_all_unique(sections, test_section)  # look at all the unique indexes in this collection.
    test_section["year"] = 1000
    test_try(sections, test_section, 'Bad year')
    # set up for a bad semester name
    test_section["year"] = 2023
    test_section["semester"] = 'Festivus'
    test_try(sections, test_section, 'Bad Semester')
    # Set up for uniqueness constraint violation
    test_section["semester"] = 'Fall'  # restore the old value
    test_section["building"] = 'ECS'  # Different building, but still violates the uniqueness constraint
    test_try(sections, test_section, 'Uniqueness constraint violation')

    test_section["year"] = 2024  # get past the uniqueness constraint violation
    test_section["course_number"] = 521
    test_section["room"] = 50
    test_section["building"] = "E1"
    test_try(sections, test_section, 'Several validation errors at once')
    print('Just supplying a value for schedule and year.')
    test_section_empty = {
        'schedule': 'S',
        'year': 2023
    }
    check_all_unique(sections, test_section_empty)
