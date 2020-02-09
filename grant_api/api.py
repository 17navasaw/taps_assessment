from flask import Flask, request
from flask_restful import Resource, Api
import flaskext.mysql as mysql
from flask_restful import reqparse
from datetime import date
import traceback

db = mysql.MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Nickelback17?'
app.config['MYSQL_DATABASE_DB'] = 'taps_assessment'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

db.init_app(app)
api = Api(app)

def calculate_age(born_year, born_month, born_day):
    today = date.today()
    return today.year - born_year - ((today.month, today.day) < (born_month, born_day))

def parse_date(dob_str):
    year = int(dob_str.split('-')[0])
    month = int(dob_str.split('-')[1])
    day = int(dob_str.split('-')[2])

    return year, month, day

def age_under_list(age_limit, age_list):
    li = []
    for i in range(len(age_list)):
        if age_list[i] < age_limit:
            li.append(i)

    return li

def age_over_list(age_limit, age_list):
    li = []
    for i in range(len(age_list)):
        if age_list[i] > age_limit:
            li.append(i)

    return li

def contains_spouse(family_members):
    for family_member in family_members:
        if family_member['marital_status'] == 'married' and family_member['spouse'] != None:
            return True

    return False

class Households(Resource):

    # list households
    def get(self):
        try:
            conn = db.connect()
            cursor = conn.cursor()

            query_get_households = "SELECT * FROM household"
            cursor.execute(query_get_households)
            query_result = cursor.fetchall()
            households = []
            for household in query_result:
                query_get_family_members = "SELECT * FROM familymember WHERE HouseholdId=%s"
                cursor.execute(query_get_family_members, household[0])
                family_members = []
                query_family_result = cursor.fetchall()
                for family_member in query_family_result:
                    family_member_details = {
                        'Id': family_member[0],
                        "name": family_member[2],
                        "gender": family_member[3],
                        "marital_status": family_member[4],
                        "spouse": family_member[5],
                        "occupation_type": family_member[6],
                        "annual_income": family_member[7],
                        "dob": family_member[8].strftime('%Y-%m-%d')
                    }
                    family_members.append(family_member_details)

                household_obj = {'Id': household[0], 'HousingType': household[1], 'FamilyMembers': family_members}
                households.append(household_obj)

            return {'StatusCode': '200', 'Households': households}
        except Exception as e:
            print("Exception: {}".format(e))
            # return {'error': str(e)}
            return {'StatusCode': '500'}

    # add household
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('HousingType', type=str)
            args = parser.parse_args()

            conn = db.connect()
            cursor = conn.cursor()

            housetype = args['HousingType']
            query = "INSERT INTO household (HousingType) VALUES (%s)"

            arguments_list = [housetype]
            cursor.execute(query, arguments_list)
            conn.commit()

            query_get_latest_id = "SELECT * FROM household WHERE ID = (SELECT MAX(ID) FROM household)"
            cursor.execute(query_get_latest_id)
            query_result = cursor.fetchall()
            household_details = {'Id': query_result[0][0], 'HousingType': query_result[0][1]}

            cursor.close()
            conn.close()
            return {'StatusCode': '200', 'HouseholdAdded': household_details}

        except Exception as e:
            print("Exception: {}".format(e))
            # return {'error': str(e)}
            return {'StatusCode': '400'}


class Household(Resource):

    # get household
    def get(self, householdid):
        try:
            conn = db.connect()
            cursor = conn.cursor()

            householdid = int(householdid)

            query_get_household = "SELECT * FROM household WHERE ID=%s"
            cursor.execute(query_get_household, [householdid])
            query_result_household = cursor.fetchall()
            query_get_family_members = "SELECT * FROM familymember WHERE HouseholdId=%s"
            cursor.execute(query_get_family_members, householdid)
            family_members = []
            query_family_result = cursor.fetchall()
            for family_member in query_family_result:
                family_member_details = {
                    'Id': family_member[0],
                    "name": family_member[2],
                    "gender": family_member[3],
                    "marital_status": family_member[4],
                    "spouse": family_member[5],
                    "occupation_type": family_member[6],
                    "annual_income": family_member[7],
                    "dob": family_member[8].strftime('%Y-%m-%d')
                }
                family_members.append(family_member_details)
            household_details = {'Id': query_result_household[0][0], 'HousingType': query_result_household[0][1], 'FamilyMembers':family_members}

            cursor.close()
            conn.close()
            return {'StatusCode': '200', 'Household': household_details}

        except Exception as e:
            print("Exception: {}".format(e))
            # return {'error': str(e)}
            return {'StatusCode': '400'}


class FamilyMember(Resource):

    # add family member to household
    def post(self, householdid):
        try:
            family_member_data = request.get_json()
            householdid = int(householdid)

            conn = db.connect()
            cursor = conn.cursor()

            query = "INSERT INTO familymember (HouseholdId, Name, Gender, MaritalStatus, Spouse, OccupationType, AnnualIncome, DOB)" \
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            arguments_list = []
            arguments_list.append(householdid)
            arguments_list.append(family_member_data['name'])
            arguments_list.append(family_member_data['gender'])
            arguments_list.append(family_member_data['marital_status'])
            arguments_list.append(family_member_data['spouse'])
            arguments_list.append(family_member_data['occupation_type'])
            arguments_list.append(family_member_data['annual_income'])
            arguments_list.append(family_member_data['dob'])

            cursor.execute(query, arguments_list)
            conn.commit()

            cursor.close()
            conn.close()
            return {'StatusCode': '200'}

        except Exception as e:
            print("Exception: {}".format(e))
            return {'StatusCode': '400'}
            # return {'error': str(e)}


class Grants(Resource):

    # get households with grants that belong to search criteria
    def get(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            # search for total income less than this amount
            parser.add_argument('income', type=str)
            # search for this household size
            parser.add_argument('size', type=str)
            args = parser.parse_args()

            conn = db.connect()
            cursor = conn.cursor()

            household_income_limit = int(args['income'])
            household_size = int(args['size'])
            households_get = Households().get()
            households_list = households_get['Households']
            filtered_households = []
            filtered_households_income = []
            filtered_households_ages = []
            for household in households_list:
                family_members = household['FamilyMembers']
                family_size = len(family_members)
                total_income = 0
                family_ages = []
                for family_member in family_members:
                    total_income += family_member['annual_income']
                    born_year, born_month, born_day = parse_date(family_member['dob'])
                    age = calculate_age(born_year, born_month, born_day)
                    family_ages.append(age)
                if family_size == household_size and total_income <= household_income_limit:
                    filtered_households.append(household)
                    filtered_households_income.append(total_income)
                    filtered_households_ages.append(family_ages)

            income_index = 0
            age_index = 0
            # Student Encouragement Bonus age<16, <150000 total income
            seb_households = []
            # Family Togetherness Scheme age<18, husband and wife
            fts_households = []
            # Elder Bonus age>50
            eb_households = []
            # Baby Sunshine Grant age<5
            bsg_households = []
            # YOLO GST Grant <100000 total income
            ygg_households = []

            for household in filtered_households:
                total_income = filtered_households_income[income_index]
                ages = filtered_households_ages[age_index]
                family_members = household['FamilyMembers']

                if total_income < 100000:
                    ygg_households.append(household)
                if total_income < 150000:
                    relevant_family_members = []
                    age_indices = age_under_list(16, ages)
                    if len(age_indices) > 0:
                        for ind in age_indices:
                            relevant_family_members.append(family_members[ind])
                        household['FamilyMembers'] = relevant_family_members
                        seb_households.append(household)
                relevant_family_members = []
                age_indices = age_under_list(5, ages)
                if len(age_indices) > 0:
                    for ind in age_indices:
                        relevant_family_members.append(family_members[ind])
                    household['FamilyMembers'] = relevant_family_members
                    bsg_households.append(household)
                relevant_family_members = []
                age_indices = age_over_list(50, ages)
                if len(age_indices) > 0:
                    for ind in age_indices:
                        relevant_family_members.append(family_members[ind])
                    household['FamilyMembers'] = relevant_family_members
                    eb_households.append(household)
                if contains_spouse(family_members):
                    relevant_family_members = []
                    age_indices = age_under_list(18, ages)
                    if len(age_indices) > 0:
                        for ind in age_indices:
                            relevant_family_members.append(family_members[ind])
                        household['FamilyMembers'] = relevant_family_members
                        fts_households.append(household)

                income_index += 1
                age_index += 1


            # print(filtered_households)
            return {'StatusCode': '200', 'Student Encouragement Bonus': seb_households,
                    'Family Togetherness Scheme': fts_households,
                    'Elder Bonus': eb_households,
                    'Baby Sunshine Grant': bsg_households,
                    'YOLO GST Grant': ygg_households}

        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            print("Exception: {}".format(e))
            return {'StatusCode': '400'}
            # return {'error': str(e)}


api.add_resource(Grants, '/grants')
api.add_resource(Household, '/households/<householdid>')
api.add_resource(Households, '/households/add', '/households')
api.add_resource(FamilyMember, '/households/<householdid>/add')

if __name__ == '__main__':
    app.run(debug=True)
