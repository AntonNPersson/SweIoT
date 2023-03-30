from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
import Operations
import cryptography
from DatabaseLayer import GetModel
import csv, io

https = Flask(__name__)
op = Operations
cry = cryptography

# Route Names
deviceName = '/administrator/all/devices/all/tools/manager'
batchName = '/administrator/all/batches/all/tools/manager'
configName = '/administrator/all/configs/all/tools/manager'
customerName = '/administrator/all/customers/all/tools/manager'
firmwareName = '/administrator/all/firmwares/all/tools/manager'
keysName = '/administrator/all/keys/all/tools/manager'
ordersName = '/administrator/all/orders/all/tools/manager'
producersName = '/administrator/all/producers/all/tools/manager'
roleName = '/administrator/all/roles/all/tools/manager'
usersName = '/administrator/all/users/all/tools/manager'
index = '/administrator/tools/index'
csvName = '/administrator/tools/csv'
insertName = '/administrator/all/<object>/all/tools/insert'
removeName = '/administrator/all/<object>/all/tools/remove'

def GetList(name):
    # Get all items in the model with the specified name using the operation module
    items = op.GetAllObjectsInModel(name)
    # Create a list to store dictionaries representing the items
    itemsDict = []
    # Iterate through each item and convert it to a dictionary
    for item in items:
        itemDict = item.__dict__   # Convert the item to a dictionary
        itemDict.pop('_sa_instance_state', None)   # Remove the '_sa_instance_state' key from the dictionary
        itemsDict.append(itemDict)   # Append the dictionary to the itemsDict list
    # Get the keys of the first dictionary in the itemsDict list, which represent the columns of the table
    columns = itemsDict[0].keys()
    # Get the model object for the specified name
    model = GetModel(name)
    # Render the 'tableList2.html' template with the itemsDict list, columns, and model as arguments
    return render_template('tableList2.html', items=itemsDict, columns=columns, orders=model)



# App routes
@https.route(deviceName, methods=['GET'])
def DeviceList():
    return GetList('devices')

@https.route(batchName, methods=['GET'])
def BatchList():
    return GetList('batch')   

@https.route(customerName, methods=['GET'])
def CustomerList():
    return GetList('customers') 

@https.route(firmwareName, methods=['GET'])
def FirmwareList():
    return GetList('firmwares') 

@https.route(configName, methods=['GET'])
def ConfigList():
    return GetList('config') 

@https.route(keysName, methods=['GET'])
def KeyList():
    return GetList('rsakeys') 

@https.route(ordersName, methods=['GET'])
def OrderList():
    return GetList('orders') 

@https.route(producersName, methods=['GET'])
def ProducerList():
    return GetList('producers') 

@https.route(roleName, methods=['GET'])
def RoleList():
    return GetList('role') 

@https.route(usersName, methods=['GET'])
def UserList():
    return GetList('users') 

@https.route(index)
def Index():
    return render_template('toolindex.html')

@https.route(insertName, methods=['POST'])
def Insert(object):
    # retrieve form data from the HTTP request
    values = dict(request.form)
    id = values.get('id')
    if id is not None and id == '':
        values.pop('id', None)

    # check if 'password' field is in the values dictionary
    if 'password' in values:
        # replace the plain-text password value with its hashed version
        values['password'] = generate_password_hash(values['password'])
    # insert form data into the specified database table
    op.InsertToTable(object, values) 
    # print the form data to the console
    print(values)
    # return a list of all records in the specified table
    return redirect('/administrator/all/'+ object +'/all/tools/manager')


@https.route(removeName, methods=['POST'])
def Remove(object):
    # Print the form data received in the request
    print(request.form)
    # Get a list of checkedIds from the form data
    values = request.form.getlist('checkedIds[]')
    # Print the list of selected values to verify that it is not empty
    print("Selected values:", values)
    # Loop through the selected values and remove each from the table using the op.RemoveFromTable function
    for value in values:
        op.RemoveFromTable(object, value)
    # Return a refreshed list of the remaining objects in the table
    return redirect('/administrator/all/'+ object +'/all/tools/manager')



@https.route(csvName, methods=['POST'])
def Upload():
    # Try to get csvFile from name and tableName from form
    try:
        csvFile = request.files['csvFile']
        tableName = request.form['tableName']
        # Use StringIO for reading file
        with io.StringIO(csvFile.stream.read().decode("UTF8"), newline='') as csvf:
            reader = csv.reader(csvf)
            # Read first row and set columnNames
            columnNames = next(reader)  
            data = []
            for row in csv.DictReader(csvf, fieldnames=columnNames):
                convertedRow = {}
                for columnName in columnNames:
                    try:
                        columnType = op.GetTable(tableName).columns[columnName].type # Get Datatype of column
                        convertedValue = columnType.python_type(row[columnName]) # Convert variable to Datatype with value
                        convertedRow[columnName] = convertedValue # Set row to convertedValue
                    except ValueError as e:
                        print(f"Error converting value '{row[columnName]}' to {columnType}: {e}")
                        convertedRow[columnName] = None
                op.InsertToTable(tableName, convertedRow)
        return 'Upload successful', 200
    except Exception as e:
        print(e)
        return 'Error uploading CSV file', 400




if __name__ == '__main__':
    https.run(ssl_context='adhoc')