# Taps #6 Technical Assessment: Government Grant Disbursement API

## Setup
Python environment:
1. Ensure Python3 is used
2. Run the following in command line to install the following libraries:
```
    pip install flask
    pip install flask_restful
    pip install flask-mysql
```

MySQL environment:

1. Install MySQL server and setup your MySQL from [here](https://dev.mysql.com/downloads/installer/)
2. Run the MySQL server and open its command line client
3. Clone this repository to a directory of your choice
4. In the MySQL command line client, run the sql file, using the following command (assuming path in Windows 10):
    ```
        mysql> source \path\to\taps_assessment\setup.sql
    ```

## Running the API
1. From root directory of repository, change directory to grant_api:
```
    cd grant_api
```
2. In api.py, assign the app.config['MYSQL_DATABASE_USER'] and app.config['MYSQL_DATABASE_PASSWORD'] variables to your MySQL username and password
3. Run the api with this command (Check that your python3 path is added to Environment PATH):
 ```
    python api.py
```

## Assumptions and Interpretations

### Assumptions
1. POST request data in body received in JSON format for adding family member
2. Date formats are in the form YYYY-MM-DD
3. Households will contain a maximum of 1 couple and any other person below 18 is assumed to be their children
4. A married man will have his spouse in the same household

### Interpretations
For the fifth endpoint, search criteria for finding households belonging to the respective grants are exact household 
size and income limit. This means that only households with the stated household size and total annual income less than the
income limit stated will be listed.
