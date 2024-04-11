from pymongo import MongoClient

## Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['CECS-323-Spring-2024']

db.createCollection('department',
    validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'title': 'department',
            'required': ['name', 'abbreviation', 'chair_name', 'building', 'office', 'description'],
            'additionalProperties': False,
            'properties': {
                '_id': {},
                'name': {
                    'bsonType': 'string',
                    'minLength': 10,
                    'maxLength': 50,
                    'description': 'The identifier of a department'
                },
                'abbreviation': {
                    'bsonType': 'string',
                    'minLength': 1,
                    'maxLength': 6,
                    'description': 'a short string identifying just one department'
                },
                'chair_name': {
                    'bsonType': 'string',
                    'minLength': 1,
                    'maxLength': 80,
                    'description': 'The person who is in charge of the department'
                },
                'building': {
                    'bsonType': 'string',
                    'enum': ["ANAC", "CDC", "DC", "ECS", "EN2", "EN3", "EN4", "EN5", "ET", "HSCI", "NUR", "VEC"],
                    'description': 'string name of the architecture where the department head office will be'
                },
                'office': {
                    'bsonType': 'int',
                    'min': 1,
                    'description': 'Integer value identifying the office'

                },
                'description': {
                    'bsonType': 'string',
                    'minLength': 10,
                    'maxLength': 80,
                    'description': 'A sentence describing the department'
                }
            }
        }
    }
);




client.close()




