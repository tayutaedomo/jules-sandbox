import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from pynamodb.connection import Connection

# Read DynamoDB endpoint URL from environment variable
# Fallback to local endpoint if not set (for direct script execution outside dev container)
DYNAMODB_HOST = os.getenv('DYNAMODB_HOST', 'http://localhost:8001')
AWS_REGION = os.getenv('AWS_REGION', 'us-local-1') # Ensure this matches docker-compose.yml

class UserModel(Model):
    """
    A DynamoDB User Model
    """
    class Meta:
        table_name = 'PynamoDBUserTable'
        # Specifies the region and host for DynamoDB Local
        region = AWS_REGION
        host = DYNAMODB_HOST
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', 'dummy') # Ensure these match docker-compose.yml
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'dummy')

    email = UnicodeAttribute(hash_key=True)
    first_name = UnicodeAttribute()
    last_name = UnicodeAttribute()
    age = NumberAttribute(null=True)

def main():
    print(f"Connecting to DynamoDB at: {DYNAMODB_HOST} in region {AWS_REGION}")

    # Create table if it doesn't exist
    if not UserModel.exists():
        print("Creating PynamoDBUserTable...")
        UserModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        print("Table created successfully.")
    else:
        print("PynamoDBUserTable already exists.")

    # Create a new user
    try:
        print("\nAttempting to create a new user...")
        user = UserModel('test@example.com', first_name='John', last_name='Doe', age=30)
        user.save()
        print("User created successfully: test@example.com")
    except Exception as e:
        print(f"Error creating user: {e}")

    # Get the user
    try:
        print("\nAttempting to retrieve the user...")
        retrieved_user = UserModel.get('test@example.com')
        print(f"Retrieved user: {retrieved_user.first_name} {retrieved_user.last_name}, Age: {retrieved_user.age}")
    except UserModel.DoesNotExist:
        print("User test@example.com does not exist.")
    except Exception as e:
        print(f"Error retrieving user: {e}")

    # Example of querying (though not strictly a 'query' for a hash key lookup)
    print("\nListing all users (scan operation):")
    try:
        for user_item in UserModel.scan():
            print(f"  - {user_item.email}: {user_item.first_name} {user_item.last_name}, Age: {user_item.age}")
    except Exception as e:
        print(f"Error scanning users: {e}")

    # Example of updating an item
    try:
        print("\nAttempting to update the user's age...")
        user_to_update = UserModel.get('test@example.com')
        user_to_update.update(actions=[
            UserModel.age.set(31)
        ])
        print("User age updated.")
        updated_user = UserModel.get('test@example.com')
        print(f"Updated user age: {updated_user.age}")
    except UserModel.DoesNotExist:
        print("User test@example.com not found for update.")
    except Exception as e:
        print(f"Error updating user: {e}")

    # Example of deleting an item
    try:
        print("\nAttempting to delete the user...")
        user_to_delete = UserModel.get('test@example.com')
        user_to_delete.delete()
        print("User deleted successfully.")
        # Try to get the deleted user (should fail)
        UserModel.get('test@example.com')
    except UserModel.DoesNotExist:
        print("User test@example.com successfully deleted and not found.")
    except Exception as e:
        print(f"Error deleting user or confirming deletion: {e}")


if __name__ == '__main__':
    # This little hack is needed for PynamoDB to work with DynamoDB Local
    # when not using the default region for the SDK (which pynamodb might default to internally
    # if not explicitly set on the model or via environment variables recognized by boto3).
    # PynamoDB's connection handling can sometimes be tricky with local endpoints
    # if the default AWS SDK credential chain doesn't pick up the local config correctly.
    # Explicitly creating a connection object can help in some cases,
    # though for PynamoDB, Meta class configuration is usually sufficient.
    #
    # For this setup, the Meta class configuration should be primary.
    # This is more of a fallback or for debugging if connection issues arise.
    #
    # conn = Connection(host=DYNAMODB_HOST, region=AWS_REGION,
    #                   aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'dummy'),
    #                   aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'dummy'))
    #
    # if not UserModel.Meta.table_name in conn.list_tables().get('TableNames', []):
    #     UserModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True, connection=conn)
    # else:
    #    print("Table already exists, connection seems fine.")
    main()
