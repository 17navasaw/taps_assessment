from flask import Flask, request
from flask_restful import Resource, Api
import flaskext.mysql as mysql
from flask_restful import reqparse

db = mysql.MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Nickelback17?'
app.config['MYSQL_DATABASE_DB'] = 'taps_assessment'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

db.init_app(app)
api = Api(app)


class Households(Resource):

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
            return {'StatusCode': '500'}


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
            #
            # query_get_latest_id = "SELECT * FROM household WHERE ID = (SELECT MAX(ID) FROM household)"
            # cursor.execute(query_get_latest_id)
            # query_result = cursor.fetchall()
            # print(query_result)
            # household_details = {'Id': query_result[0][0], 'HousingType': query_result[0][1]}
            #
            cursor.close()
            conn.close()
            return {'StatusCode': '200'}

        except Exception as e:
            print("Exception: {}".format(e))
            return {'StatusCode': '500'}
            # return {'error': str(e)}


class Grant(Resource):

    def post(self):

        return {"status": "success"}


api.add_resource(Grant, '/grant')
api.add_resource(Households, '/households/add', '/households')
api.add_resource(FamilyMember, '/households/<householdid>/add')

if __name__ == '__main__':
    app.run(debug=True)
