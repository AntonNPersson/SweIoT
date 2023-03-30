import DatabaseLayer
import Cryptography
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func, Sequence
import logging
dl = DatabaseLayer
cry = Cryptography
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

def executeQuery(query_func, *args, **kwargs):
    # Get a database session and the SQLAlchemy Base object
    session, base = dl.GetSession()
    try:
        # Execute the query function with the session and additional arguments as arguments
        result = query_func(session, base, *args, **kwargs)
        if result is None:
            return 'Error: Could not proccess query'
        # Print a success message to indicate that the query was successful
        print('Success')
        # Return the result
        return result
    except (SQLAlchemyError, IntegrityError, ValueError, AssertionError, TypeError, AttributeError) as e:
        # If an error occurs, rollback the session and return the error
        session.rollback()
        print(str(e))
        return 'Failure' 
    finally:
        # Close the session
        session.close()

def GetSpecificFromColumnInTable(value, column, table):
    def queryFunc(session, base, value, column, table):
        # Check if value is provided
        assert value is not None, "Error: No value provided"
        # Get all rows from the specified table and column
        theTable = GetAllOfColumnFromTable(table, column)
        # Check if an error occurred during retrieval
        if(theTable == False):
            return 'Error: No table exist with provided values'
        # If no error, query the row that matches the provided value
        else:
            return theTable.query.filter_by(value).first()
    return executeQuery(queryFunc, value, column, table)


# Add to any table to the database. Currently checks if missing columns and database constraints
def InsertToTable(table, values):
    def queryFunc(session, base, values):
        # Get table model and columns
        name = "public." + table
        tableModel = base.metadata.tables.get(name)
        # Check if table exists
        if tableModel is None:
            return False, 'Error: Table not found'
        columnsModel = tableModel.columns.keys()
        newValues = {}
        # Ensure that values are provided
        assert values is not None, "Error: No values provided"
        # Loop through the columns in the table and create a dictionary
        # with column names and values to insert
        for column in columnsModel:
            if column in values:
                newValues[column] = values[column]
            elif column == 'id':
                # Generate a new id value using the default sequence
                query = f"SELECT nextval('{table}_id_seq')"
                result = session.execute(query)
                newValues[column] = result.scalar()
            else:
                newValues[column] = None  # Use default value for missing columns
        # Insert the new object into the table
        newObject = tableModel.insert().values(**newValues)
        session.execute(newObject)
        session.commit()
        # Return success
        return True
    return executeQuery(queryFunc, values)

def RemoveFromTable(table, id):
    def queryFunc(session, base, table, id):
        # Get the table model from the metadata based on the provided table name
        name = "public." + table
        tableModel = base.metadata.tables.get(name)
        # Check if the table exists in the metadata
        if tableModel is None:
            return False, 'Error: Table not found'
        # Ensure that an ID is provided
        assert id is not None, "Error: No ID provided"
        # Create a query to remove a row with the given ID from the table
        query = tableModel.delete().where(tableModel.c.id == id)
        # Execute the query and commit the transaction
        session.execute(query)
        session.commit()
        return True
    return executeQuery(queryFunc, table, id)

def GetAllObjectsInModel(modelName):
    # Connect to database
    session, base = dl.GetSession()
    # If session or base is None, return error message
    if session is None or base is None:
        return False, 'Unable to connect to database'
    try:
    # Retrieve all rows from the specified database model
        rows = session.query(dl.GetModel(modelName)).all()
    # If there are no rows, return error message
        if not rows:
            return False, 'The list is empty'
    # Return the rows
        return rows
    except (SQLAlchemyError, IntegrityError, ValueError, AssertionError, TypeError) as e:
    # If there is an error, rollback the session, print the error and return it
        session.rollback()
        print("Error:", e)
        return False, e
    finally:
    # Close the session
        session.close()


def GetAllFromTable(tableName):
    def queryFunc(session, base, tableName):
        # Construct the full table name
        realName = "public." + tableName
        # Get the table object for the specified table name
        tableObject = base.metadata.tables.get(realName)
        # Check if the table object exists
        if tableObject is None:
            return False, 'Error: Table not found'
        # Query the table object and return the results
        objects = session.query(tableObject).all()
        if not objects:
            return False, 'The provided table is empty'
        return objects
    return executeQuery(queryFunc, tableName)

def GetTable(tableName):
    def queryFunc(session, base, tableName):
        # Construct the full table name (including schema) and use it to create a table object
        realName = "public." + tableName
        table = dl.CreateTableObject(realName, base.metadata)
        return table
    return executeQuery(queryFunc, tableName)


def GetAllOfColumnFromTable(tableName, columnName):
    def queryFunc(session, base, tableName, columnName):
        realName = "public." + tableName
        # Get the Table object for the specified table name
        table = base.metadata.tables.get(realName)
        for table_name in base.metadata.tables.keys():
            print(table_name)
        if table is None:
            return False, 'Table "{}" does not exist'.format(tableName)
        # Get the Column object for the specified column name
        column = table.columns.get(columnName)
        if column is None:
            return False, 'Column "{}" does not exist in table "{}"'.format(columnName, tableName)
        # Query the database to retrieve all values in the specified column
        result = session.query(column).all()
        return result
    return executeQuery(queryFunc, tableName, columnName)

def AddKeyPairFromDevice(privateKey, publicKey, deviceId):
    def queryFunc(session, base, privateKey, publicKey, deviceId):
        # Validate inputs
        if not privateKey:
            raise ValueError("Private key is empty")
        if not publicKey:
            raise ValueError("Public key is empty")
        if not deviceId:
            raise ValueError("Device ID is empty")
        # Find customerid from devideid (temporary until auth working)
        device = session.query(dl.Devices(base)).filter_by(id=deviceId).first()
        if not device:
            raise ValueError("No device found with device ID: " + deviceId) 
        customerId = device.customer_id
        # Insert keys into database
        keysTable = base.metadata.tables.get('public.rsakeys')
        existingKey = session.query(keysTable).filter_by(device_id=deviceId).first()
        if existingKey:
            raise ValueError("Key pair already exist for device with ID: " + deviceId)
        newKeys = keysTable.insert().values(privatekey=privateKey, publickey=publicKey, device_id=deviceId, customer_id=customerId)
        session.execute(newKeys)
        session.commit()
        print('Key pair added successfully')
        return 'Key pair added successfully'
    return executeQuery(queryFunc, privateKey, publicKey, deviceId)

def AddKeyPairFromMac(privateKey, publicKey, mac):
    def queryFunc(session, base, privateKey, publicKey, mac):
        # Hash key values
        hashedPrK = cry.PemToHash(privateKey)
        hashedPuB = cry.PemToHash(publicKey)
        # Look up device ID and customer ID from database using MAC address
        device = session.query(dl.Devices(base)).filter_by(mac_adress=mac).first()
        if not device:
            raise ValueError("No device found with MAC address " + mac)
        deviceId = device.id
        customerId = device.customer_id
        # Create table object and insert new keys
        keysTable = base.metadata.tables.get('public.rsakeys')
        existingKey = session.query(keysTable).filter_by(device_id=deviceId).first()
        if existingKey:
            raise ValueError("Key pair already exist for device with ID: " + deviceId)
        newKeys = keysTable.insert().values(privatekey=hashedPrK, publickey=hashedPuB, device_id=deviceId, customer_id=customerId)
        session.execute(newKeys)
        session.commit()
        print('success')
        return 'Success'
    return executeQuery(queryFunc, privateKey, publicKey, mac)
    
def GetPrivateKeyFromMAC(mac):
    def queryFunc(session, base, mac):
       # Query the database to get the device object by its MAC address
        device = session.query(dl.Devices(base)).filter_by(mac_adress=mac).first()
        # Query the database to get the key object associated with the device
        Key = session.query(dl.GetKeys(base)).filter_by(device_id=device.id).first()
        # Convert the private key to a PEM format
        pem_key = cry.HashToPem(Key.privatekey, 'RSA Private Key')
        # Return the PEM formatted private key
        print('Success')
        return pem_key
    return executeQuery(queryFunc, mac)
    
def GetPrivateKeyFromID(id):
    def queryFunc(session, base, id):
        # Query the database for the private key associated with the provided ID
        Key = session.query(dl.GetKeys(base)).filter_by(device_id=id).first()
        print('Success')
        # Return the private key
        return Key.privatekey
    return executeQuery(queryFunc, id)
    
def GetPublicKeyFromID(id):
    def queryFunc(session, base, id):
        # Query the keys table to get the key with the specified device_id
        Key = session.query(dl.GetKeys(base)).filter_by(device_id=id).first()
        # Print a success message to indicate that the key was found
        print('Success')
        # Return the public key as a PEM-encoded string
        return cry.HashToPem(Key.publickey, 'RSA Public Key')
    return executeQuery(queryFunc, id)
