# MongoDB-Schema-Uniqueness

This project provide hands-on experience in constraining a MongoDB collection. By adding validators and uniqueness constraints, the objective is to enforce business rules and protect the database from erroneous data.this project delves deeper into enhancing the collection by implementing constraints. Moon Modeler, a visualization tool, will be utilized to generate validators and uniqueness constraints for the Departments collection.

Procedure:

- Reverse Engineer from Atlas into Moon Modeler: Moon Modeler will query MongoDB to import metadata and visualize existing collections.

- Enhance the Departments Collection: Add constraints to the model based on business rules and requirements. Constraints include limiting building values, specifying attribute lengths, and enforcing attribute presence.

- Add Uniqueness Constraints: Define indexes in Moon Modeler to ensure uniqueness for specific attributes. Uniqueness constraints include name, abbreviation, chair_name, and the combination of building and office.

- Implement Validators and Uniqueness Constraints: Incorporate validators and uniqueness constraints into the collection. Modify Moon Modeler-generated code for compatibility with Python.

- Error Handling: Implement try/except blocks in Python code to catch constraint violations. Prompt the user to re-enter input if constraints are violated, ensuring data integrity without preventing input.

Key Considerations:

- Schema Definition: Establishing constraints to maintain data consistency and integrity.

- Uniqueness Constraints: Ensuring uniqueness for specific attributes to prevent duplicate data.

- Error Handling: Utilizing Python's try/except blocks to capture and handle constraint violations gracefully.

- User Interaction: Providing users with opportunities to correct input errors without interrupting their workflow.

Tools Required:

MongoDB Atlas: To reverse engineer existing collections. Moon Modeler: For visual representation and generation of validators and uniqueness constraints. Python IDE (e.g., PyCharm): For implementing validators, uniqueness constraints, and error handling.

This project gain me practical experience in implementing schema and uniqueness constraints in MongoDB collections, enhancing their understanding of database management and data integrity principles.
