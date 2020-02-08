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
    # def get(self):


    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('HousingType', type=str)
            args = parser.parse_args()

            conn = db.connect()
            cursor = conn.cursor()

            housetype = args['HousingType']
            print(housetype)
            query = "INSERT INTO household (HousingType) VALUES (%s)"

            arguments_list = [housetype]
            cursor.execute(query, arguments_list)
            conn.commit()

            query_get_latest_id = "SELECT * FROM household WHERE ID = (SELECT MAX(ID) FROM household)"
            cursor.execute(query_get_latest_id)
            query_result = cursor.fetchall()
            print(query_result)
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
