import pymongo
from pymongo import MongoClient
from pprint import pprint
import getpass
from menu_definitions import menu_main
from menu_definitions import add_menu
from menu_definitions import delete_menu
from menu_definitions import list_menu

import io
from pymongo.errors import DuplicateKeyError
from pymongo.errors import WriteError
from pprint import pprint
from bson.objectid import ObjectId

def add(db):
    """
    Present the add menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    add_action: str = ''
    while add_action != add_menu.last_action():
        add_action = add_menu.menu_prompt()
        exec(add_action)

def delete(db):
    """
    Present the delete menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    delete_action: str = ''
    while delete_action != delete_menu.last_action():
        delete_action = delete_menu.menu_prompt()
        exec(delete_action)

def list_objects(db):
    """
    Present the list menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    list_action: str = ''
    while list_action != list_menu.last_action():
        list_action = list_menu.menu_prompt()
        exec(list_action)

def add_student(db):
    """
    Add a new student, making sure that we don't put in any duplicates,
    based on all the candidate keys (AKA unique indexes) on the
    students collection.  Theoretically, we could query MongoDB to find
    the uniqueness constraints in place, and use that information to
    dynamically decide what searches we need to do to make sure that
    we don't violate any of the uniqueness constraints.  Extra credit anyone?
    :param collection:  The pointer to the students collection.
    :return:            None
    """
    # Create a "pointer" to the students collection within the db database.
    collection = db["students"]
    unique_name: bool = False
    unique_email: bool = False
    lastName: str = ''
    firstName: str = ''
    email: str = ''
    while not unique_name or not unique_email:
        lastName = input("Student last name--> ")
        firstName = input("Student first name--> ")
        email = input("Student e-mail address--> ")
        name_count: int = collection.count_documents({"last_name": lastName, "first_name": firstName})
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a student by that name.  Try again.")
        if unique_name:
            email_count = collection.count_documents({"e_mail": email})
            unique_email = email_count == 0
            if not unique_email:
                print("We already have a student with that e-mail address.  Try again.")
    # Build a new students document preparatory to storing it
    student = {
        "last_name": lastName,
        "first_name": firstName,
        "e_mail": email
    }
    results = collection.insert_one(student)

def select_student(db):
    """
    Select a student by the combination of the last and first.
    :param db:      The connection to the database.
    :return:        The selected student as a dict.  This is not the same as it was
                    in SQLAlchemy, it is just a copy of the Student document from
                    the database.
    """
    # Create a connection to the students collection from this database
    collection = db["students"]
    found: bool = False
    lastName: str = ''
    firstName: str = ''
    while not found:
        lastName = input("Student's last name--> ")
        firstName = input("Student's first name--> ")
        name_count: int = collection.count_documents({"last_name": lastName, "first_name": firstName})
        found = name_count == 1
        if not found:
            print("No student found by that name.  Try again.")
    found_student = collection.find_one({"last_name": lastName, "first_name": firstName})
    return found_student

def delete_student(db):
    """
    Delete a student from the database.
    :param db:  The current database connection.
    :return:    None
    """
    # student isn't a Student object (we have no such thing in this application)
    # rather it's a dict with all the content of the selected student, including
    # the MongoDB-supplied _id column which is a built-in surrogate.
    student = select_student(db)
    # Create a "pointer" to the students collection within the db database.
    students = db["students"]
    # student["_id"] returns the _id value from the selected student document.
    deleted = students.delete_one({"_id": student["_id"]})
    # The deleted variable is a document that tells us, among other things, how
    # many documents we deleted.
    print(f"We just deleted: {deleted.deleted_count} students.")

def list_student(db):
    """
    List all of the students, sorted by last name first, then the first name.
    :param db:  The current connection to the MongoDB database.
    :return:    None
    """
    # No real point in creating a pointer to the collection, I'm only using it
    # once in here.  The {} inside the find simply tells the find that I have
    # no criteria.  Essentially this is analogous to a SQL find * from students.
    # Each tuple in the sort specification has the name of the field, followed
    # by the specification of ascending versus descending.
    students = db["students"].find({}).sort([("last_name", pymongo.ASCENDING),
                                             ("first_name", pymongo.ASCENDING)])
    # pretty print is good enough for this work.  It doesn't have to win a beauty contest.
    for student in students:
        pprint(student)


def add_department(db):
    collection = db["departments"]

    while True:
        try:
            name = input("Department name--> ")
            abbreviation = input("Department abbreviation--> ")
            chair_name = input("Chair name--> ")
            building = input("Building--> ")
            office = int(input("Office--> "))
            description = input("Description--> ")

            # Check for uniqueness
            existing_department = collection.find_one({
                "$or": [
                    {"name": name},
                    {"abbreviation": abbreviation},
                    {"chair_name": chair_name},
                    {"building": building, "office": office},
                    {"description": description}
                ]
            })

            if existing_department:
                print("Department with one of the provided details already exists. Try again.")
                continue

            # Build and insert the department document
            department = {
                "name": name,
                "abbreviation": abbreviation,
                "chair_name": chair_name,
                "building": building,
                "office": office,
                "description": description,
            }
            collection.insert_one(department)
            print("Department added successfully.")
            break

        except ValueError:
            print("Please enter a valid office number.")
        except Exception as e:
            print("An error occurred:", e)


def select_department(db):

    # Create a connection to the students collection from this database
    collection = db["departments"]
    found: bool = False
    abbreviation: str = ''
    while not found:
        abbreviation = input("Enter the department abbreviation--> ")
        abbreviation_count: int = collection.count_documents({"abbreviation": abbreviation})
        found = abbreviation_count == 1
        if not found:
            print("No department with that abbreviation.  Try again.")
    found_department = collection.find_one({"abbreviation": abbreviation})
    return found_department

def delete_department(db):
    department = select_department(db)
    # Create a "pointer" to the students collection within the db database.
    departments = db["departments"]

    deleted = departments.delete_one({"name": department["name"]})

    print(f"We just deleted: {deleted.deleted_count} department.")

def list_department(db):

    departments = db["departments"].find({}).sort([("name", pymongo.ASCENDING),
                                             ("abbreviation", pymongo.ASCENDING),
                                             ("chair_name", pymongo.ASCENDING),
                                             ("building", pymongo.ASCENDING),
                                             ("office", pymongo.ASCENDING),
                                             ("description", pymongo.ASCENDING)])
    # pretty print is good enough for this work.  It doesn't have to win a beauty contest.
    for department in departments:
        pprint(department)

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
                    f"Unique index: {index} will be respected: {check_unique(departments, new_document, columns['key'])}")


if __name__ == '__main__':

    # password: str = getpass.getpass('Mongo DB password -->')
    # username: str = input('Database username [CECS-323-Spring-2023-user] -->') or \
    #                 "CECS-323-Spring-2023-user"
    # project: str = input('Mongo project name [cecs-323-spring-2023] -->') or \
    #                "CECS-323-Spring-2023"
    # hash_name: str = input('7-character database hash [puxnikb] -->') or "puxnikb"

    # Login ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    password = ""
    username = ""
    project = ""
    hash_name = ""
    # Login ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    cluster = f"mongodb+srv://{username}:{password}@{project}.{hash_name}.mongodb.net/?retryWrites=true&w=majority"
    print(f"Cluster: mongodb+srv://{username}:********@{project}.{hash_name}.mongodb.net/?retryWrites=true&w=majority")
    client = MongoClient(cluster)
    # As a test that the connection worked, print out the database names.
    print(client.list_database_names())
    # db will be the way that we refer to the database from here on out.
    db = client["SchemaUniqueness"]
    # Print off the collections that we have available to us, again more of a test than anything.
    print(db.list_collection_names())
    # department is our departments collection within this database.
    # Merely referencing this collection will create it, although it won't show up in Atlas until
    # we insert our first document into this collection.
    # Connect to MongoDB Atlas

    departments = db["departments"]

    choice = -1
    done = False
    while not done:
        print("Would you like to: \n1. Use an existing collection \n2. Start from scratch")
        choice = int(input("Choice: "))

        if choice == 1:
            # Check if there are any documents in the "departments" collection
            if db.departments.count_documents({}) > 0:
                print("Using existing 'departments' collection.\n")

                department_count = departments.count_documents({})
                print(f"Departments in the collection so far: {department_count}")

                done = True
            else:
                print("No existing collections found.\n")

        elif choice == 2:

            departments_validator = {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': "object",
                        'title': "department",
                        'required': ["name", "abbreviation", "chair_name", "building", "office", "description"],
                        'additionalProperties': False,
                        'properties': {
                            '_id': {},
                            'name': {
                                'bsonType': "string",
                                'minLength': 10,
                                'maxLength': 50,
                                "description": "The identifier of a department"
                            },
                            'abbreviation': {
                                'bsonType': "string",
                                'minLength': 1,
                                'maxLength': 6,
                                "description": "a short string identifying just one department"
                            },
                            'chair_name': {
                                'bsonType': "string",
                                'minLength': 1,
                                'maxLength': 80,
                                "description": "The person who is in charge of the department"
                            },
                            'building': {
                                'bsonType': "string",
                                'enum': ["ANAC", "CDC", "DC", "ECS", "EN2", "EN3", "EN4", "EN5", "ET", "HSCI", "NUR", "VEC"],
                                "description": "string name of the architecture where the department head office will be"
                            },
                            'office': {
                                'bsonType': "int",
                                'minimum': 1,
                                "description": "Integer value identifying the office"

                            },
                            'description': {
                                'bsonType': "string",
                                'minLength': 10,
                                'maxLength': 80,
                                "description": "A sentence describing the department"
                            }
                        }
                    }
                }
            }

            if "departments" in db.list_collection_names():
                print("dropping the departments collection.")
                departments.drop()

            print(db.create_collection("departments", **departments_validator))

            # We cannot have two departments with the same name, abbreviation, chair_name, building, and office
            departments.create_index([("name", pymongo.ASCENDING), ("abbreviation", pymongo.ASCENDING),
                                   ("chair_name", pymongo.ASCENDING), ("building", pymongo.ASCENDING),
                                   ("office", pymongo.ASCENDING)], unique=True, name='departments_uk_01')

            departments_indexes = departments.index_information()

            if 'name' in departments_indexes.keys():
                print("name and abbr index present.")
            else:
                # Create a single UNIQUE index
                departments.create_index([('name', pymongo.ASCENDING)], unique=True, name='name')

            if 'abbreviation' in departments_indexes.keys():
                print("chair_name index present.")
            else:
                # Create a UNIQUE index on just the abbreviation
                departments.create_index([('abbreviation', pymongo.ASCENDING)], unique=True, name='abbreviation')

            if 'chair_name' in departments_indexes.keys():
                print("chair_name index present.")
            else:
                # Create a UNIQUE index on just the chair_name
                departments.create_index([('chair_name', pymongo.ASCENDING)], unique=True, name='chair_name')

            if 'building_office' in departments_indexes.keys():
                print("building and office index present.")
            else:
                # Create a UNIQUE index on both the building and office
                departments.create_index([('building', pymongo.ASCENDING), ('office', pymongo.ASCENDING)], unique=True,
                                         name='building_office')

            done = True

        else:
            print("Invalid input, choose either 1 or 2")

    pprint(departments.index_information())
    main_action: str = ''

    while main_action != menu_main.last_action():
        main_action = menu_main.menu_prompt()
        print('next action: ', main_action)
        exec(main_action)

