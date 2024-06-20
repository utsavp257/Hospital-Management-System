import json
import time
import sys

sys.path.append("..")  # Adds higher directory to python modules path.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
# backend
# Importing Package
import sqlalchemy
# Database Utility Class
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
from rest_framework.response import Response



class PostgresqlDB:
    def __init__(self, user_name, password, host, port, db_name):
        """
        class to implement DDL, DQL and DML commands,
        user_name:- username
        password:- password of the user
        host
        port:- port number
        db_name:- database name
        """
        self.user_name = user_name
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.engine = self.create_db_engine()
        print(f'internal login {user_name}')

    def create_db_engine(self):
        """
        Method to establish a connection to the database, will return an instance of Engine
        which can used to communicate with the database
        """
        try:
            db_uri = f"postgresql+psycopg2://{self.user_name}:{self.password}@{self.host}:{self.port}/{self.db_name}"
            return create_engine(db_uri)
        except Exception as err:
            raise RuntimeError(f'Failed to establish connection -- {err}') from err

    def execute_dql_commands(self, stmnt, values=None):
        """
        DQL - Data Query Language
        SQLAlchemy execute query by default as

        BEGIN
        ....
        ROLLBACK

        BEGIN will be added implicitly everytime but if we don't mention commit or rollback explicitly
        then rollback will be appended at the end.
        We can execute only retrieval query with above transaction block.If we try to insert or update data
        it will be rolled back.That's why it is necessary to use commit when we are executing
        Data Manipulation Langiage(DML) or Data Definition Language(DDL) Query.
        """
        try:
            with self.engine.connect() as conn:
                if values is not None:
                    result = conn.execute(text(stmnt), values)
                else:
                    result = conn.execute(text(stmnt))
            return result
        except Exception as err:
            print(f'Failed to execute dql commands -- {err}')
            return -1

    def execute_ddl_and_dml_commands(self, stmnt, values=None):
        """
        Method to execute DDL and DML commands
        here we have followed another approach without using the "with" clause
        """
        connection = self.engine.connect()
        trans = connection.begin()
        try:
            if values is not None:

                result = connection.execute(text(stmnt), values)
            else:
                result = connection.execute(text(stmnt))
            trans.commit()
            connection.close()
            print('Command executed successfully.')
            return 0
        except Exception as err:
            trans.rollback()
            print(f'Failed to execute ddl and dml commands -- {err}')
            return -1


# Defining Db Credentials
USER_NAME = 'postgres'
PASSWORD = 'postgres'
PORT = 5432
DATABASE_NAME = 'dbms_final1'
HOST = 'localhost'

# Note - Database should be created before executing below operation
# Initializing SqlAlchemy Postgresql Db Instance
db = PostgresqlDB(user_name=USER_NAME,
                  password=PASSWORD,
                  host=HOST, port=PORT,
                  db_name=DATABASE_NAME)
engine = db.engine
print('idk when this runs')


# Create your views here.
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        try:
            login_query = f'set role postgres;'
            print(login_query)
            db.execute_ddl_and_dml_commands(login_query)
            data = request.data
            print(data)
            user_id = data['username'].strip()
            password = data['password']
            role = data['role']
            USER_NAME = user_id.lower()

            # Note - Database should be created before executing below operation
            # Initializing SqlAlchemy Postgresql Db Instance
            # db = PostgresqlDB(user_name=USER_NAME,
            #                   password=PASSWORD,
            #                   host=HOST, port=PORT,
            #                   db_name=DATABASE_NAME)
            # engine = db.engine

            print(f"logged in as {USER_NAME}")
            print(user_id)
            if role == 'Admin':
                if user_id[:2] != 'SA':
                    return Response({
                        'status': 420,
                        'message': "invalid role"
                    })
                q2 = f"SELECT \
                        CASE \
                        WHEN EXISTS (select * from system_administrator where admin_id = '{user_id}' and a_password = '{password}') THEN 1 \
                        ELSE 0 \
                        END AS result;"
                result = db.execute_dql_commands(q2)
                time.sleep(0.5)
                for row in result:
                    if row[0] == 0:
                        return Response({
                            'status': 420,
                            'message': "invalid user id or password",
                        })
            else:
                if user_id[0] != role[0].upper():
                    return Response({
                        'status': 420,
                        'message': "invalid role"
                    })
                # q1 = f"select * from user_table where user_id = '{user_id}' and u_password = '{password}';"
                q2 = f"SELECT \
                       CASE \
                       WHEN EXISTS (select * from user_table where user_id = '{user_id}' and u_password = '{password}') THEN 1 \
                       ELSE 0 \
                       END AS result;"
                result = db.execute_dql_commands(q2)
                time.sleep(0.5)
                for row in result:
                    if row[0] == 0:
                        return Response({
                            'status': 420,
                            'message': "invalid user id or password",
                        })

            # for row in result:
            #     print("hi", row)
            login_query = f'set role {USER_NAME};'
            print(login_query)
            db.execute_ddl_and_dml_commands(login_query)

            q2 = f"SELECT current_user;"
            result = db.execute_dql_commands(q2)
            for row in result:
                print(f"Currently Logged in as {row[0]}")
            time.sleep(0.5)
            return Response(
                {
                    'status': 200,
                    'username': user_id,
                    'role': role,
                }
            )
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'Internal error, server error',
            })


def patient_view(request, number):
    # return HttpResponse(f"Patient ID is {number}")
    return render(request, 'patient_page/patient.html', {'name': number})


def reception_view(request, number):
    # return HttpResponse(f"Patient ID is {number}")
    return render(request, 'receptionist_page/receptionist.html', {'name': number})


def staff_view(request, number):
    # return HttpResponse(f"Patient ID is {number}")
    return render(request, 'staff_page/staff.html', {'name': number})


def doctor_view(request, number):
    # return HttpResponse(f"Patient ID is {number}")
    return render(request, 'doctor_page/doctor.html', {'name': number})


def admin_view(request, number):
    # return HttpResponse(f"Admin ID is {number}")
    return render(request, 'admin_page/admin.html', {'name': number})


# @api_view(['GET'])
# def patient_view(request):
#     # Retrieve patient ID from query parameters
#     patient_id = request.GET.get('user_id')
#     if patient_id is not None:
#         # Use patient ID to fetch patient data from the database
#         patient = UserTable.objects.get(pk=patient_id)
#         # Pass patient data to the template
#         return render(request, 'patient.html', {'patient': patient})
#     else:
#         # Handle invalid request (no patient ID provided)
#         return HttpResponse("Patient ID not provided")


@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        try:
            data = request.data
            print(data)
            f_name = data['firstName']
            l_name = data['lastName']
            gender = data['gender']
            phone = data['phone']
            password1 = data['password']
            dob = data['dob']
            address = data['address']
            b_group = data['bloodGroup']
            # role = data['role']
            q1 = f"select user_id from user_table where user_id like 'P%';"
            result = db.execute_dql_commands(q1)
            time.sleep(1)
            p_id = []
            for row in result:
                p_id.append(row[0])
            if len(p_id) == 0:
                new_id = 'P001'
            else:
                res = []
                for i in p_id:
                    i = i.replace(i[0], "", 1)
                    i = int(i)
                    res.append(i)
                print(res)
                res.sort(reverse=True)
                new_id = res[0] + 1
                new_id = 'P' + f'{new_id:03d}'
                print(new_id)
            q2 = f"""
                    begin;

                    insert into user_table(user_id,u_password,fname,lname,gender,phone_no)
                    values('{new_id}','{password1}','{f_name}','{l_name}','{gender[0].upper()}','{phone}');

                    insert into inpatient(patient_id,fname,lname,gender,date_of_birth,address,blood_group)
                    values('{new_id}','{f_name}','{l_name}','{gender[0].upper()}','{dob}','{address}','{b_group}');
                    drop user if exists {new_id};
                    create user {new_id} WITH PASSWORD 'postgres';

                    GRANT patient TO {new_id};

                    commit;
                    """
            db.execute_ddl_and_dml_commands(q2)
            time.sleep(1)
            print("inserted", new_id)
            res = Response({
                'status': 200,
                'Login_id': new_id
            })
            print(res)
            return res
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'Internal error, server error'
            })


# receptionist starts here
@api_view(['GET'])
def view_appointment_requests(request):
    if request.method == 'GET':
        try:
            # Execute query to fetch all entries from req_appointments table
            query = "SELECT * FROM viewAppointmentReqRec();"
            result = db.execute_dql_commands(query)

            # Convert the result to a list of dictionaries
            appointments = []
            for row in result:
                appointment = {
                    'serial_id': row[0],
                    'patient_id': row[1],
                    'rec_id': row[2],
                    'symptoms': row[3],
                    't_stamp': row[4],

                    # Add more fields as needed
                }
                appointments.append(appointment)
            print(appointments)
            return Response({
                'status': 200,
                'appointments': appointments
            })
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'Internal server error'
            })


@api_view(['GET'])
def get_doctor_details(request):
    if request.method == 'GET':
        # Get the doctor_id from the query parameters
        doctor_spec = request.GET.get('doctor_spec')

        if doctor_spec is not None:
            try:
                # Execute query to fetch doctor details
                query = f'''SELECT * FROM viewDocDetailsRec('{doctor_spec}');'''
                result = db.execute_dql_commands(query)
                time.sleep(0.01)
                print("Idhar ghusa ki nahi?")
                # print(doctor_id)
                # Check if doctor details are found
                doctor_details = []

                for row in result:
                    doctor_details.append({
                        'doctor_id': row[0],
                        'fname': row[1],
                        'lname': row[2],
                        'gender': row[3],
                        'qualification': row[4],
                        'dtype': row[5],
                        'phone_no': row[6]
                        # Add more fields as needed
                    })
                return JsonResponse({'status': 'success', 'doctor_details': doctor_details})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Doctor ID parameter missing'}, status=400)


@csrf_exempt
@api_view(['POST'])
def create_appointment(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body

            flag = 0
            q1 = f"select appointment_id from appointment_schedule where appointment_id like 'A%';"
            result = db.execute_dql_commands(q1)
            time.sleep(1)
            p_id = []
            new_id = 'A001'
            len_result = 0
            for row in result:
                len_result += 1
                p_id.append(row[0])
            print(f'lenresult is {len_result}')
            if len_result == 0:
                new_id = 'A001'
            else:
                print("Else me ghusa")
                res = []
                print(len(p_id))
                for i in p_id:
                    i = i.replace(i[0], "", 1)
                    # print(type(i))
                    # print(i)
                    i = int(float(i))
                    res.append(i)
                if len(res) == 0:
                    res.append(1)
                    flag = 1
                print(res)
                res.sort(reverse=True)
                if flag == 0:
                    new_id = res[0] + 1
                new_id = 'A' + f'{new_id:03d}'
            print(f'new_id is {new_id}')

            data = json.loads(request.body)
            doctor_id = data.get('doctor_id')
            patient_id = data.get('patient_id')
            print(data)
            doc_check = f''' select * from viewDoctorDetails where doctor_id = '{doctor_id}';'''
            result = db.execute_dql_commands(doc_check)
            len_check = 0
            for row in result:
                len_check += 1
                print(row[0])
            if len_check==0:
                return JsonResponse({'status': 'error', 'message': 'The doctor does not exist'},
                                    status=500)
            if result==-1:
                return JsonResponse({'status': 'error', 'message': 'The doctor does not exist'},
                                    status=500)

            patient_check = f''' select * from viewAppointmentReqRec() where patient_id = '{patient_id}';'''
            result = db.execute_dql_commands(patient_check)
            len_check = 0
            for row in result:
                len_check += 1
                print(row[0])
            if len_check == 0:
                return JsonResponse({'status': 'error', 'message': 'There is no request for this patient_id'},
                                    status=500)
            if result==-1:
                return JsonResponse({'status': 'error', 'message': 'There is no request for this patient_id'},
                                    status=500)
            # Extract appointment details from the data
            # appointment_id = data.get('appointment_id')
            appointment_date = data.get('appointment_date')
            appointment_time = data.get('appointment_time')
            doctor_id = data.get('doctor_id')
            patient_id = data.get('patient_id')
            symptoms = data.get('symptoms')
            appointment_status = data.get('appointment_status')

            # Check if the doctor is available at the requested time
            sql_check_availability = f"""
                                        SELECT CASE WHEN EXISTS (
                                            SELECT 1 
                                            FROM appointment_schedule 
                                            WHERE doctor_id = '{doctor_id}' 
                                                AND appointment_date = '{appointment_date}' 
                                                AND (appointment_time <= '{appointment_time}' 
                                                AND '{appointment_time}' < (appointment_time + INTERVAL '1 hour'))
                                        ) THEN 1 ELSE 0 END
                                    """

            # Execute the SQL statement to check doctor availability
            result_availability = db.execute_dql_commands(sql_check_availability)
            check_ans = 0
            for row in result_availability:
                check_ans = int(row[0])
            if check_ans == 1:
                return JsonResponse({'status': 'error', 'message': 'The doctor is busy at the selected moment'}, status=500)

            # Extract appointment details from the data
            # appointment_id = data.get('appointment_id')
            appointment_date = data.get('appointment_date')
            appointment_time = data.get('appointment_time')
            doctor_id = data.get('doctor_id')
            patient_id = data.get('patient_id')
            symptoms = data.get('symptoms')
            appointment_status = data.get('appointment_status')
            # Convert appointment_date and appointment_time to datetime objects
            print("Nanga naach")



            # Define the SQL statement to insert into appointment_schedule table
            sql_insert = f"""
                begin;
                SELECT insertAppointmentSchedule('{new_id}', '{appointment_date}', '{appointment_time}', '{doctor_id}', '{patient_id}', '{symptoms}', 'Pending'); 
                commit;
            """

            # Execute the SQL statement with parameters using db.execute_ddl_and_dml_commands
            db.execute_ddl_and_dml_commands(sql_insert)
            time.sleep(1)
            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Appointment created successfully'})
        except Exception as e:
            # Return an error response if there's an exception
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        # Return an error response for unsupported request methods
        return JsonResponse({'status': 'error', 'message': 'Unsupported request method'}, status=405)


@api_view(['POST'])
def assign_ward(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            data = request.data
            patient_id = data.get('patient_id')
            ward_id = data.get('ward_id')
            # available_beds = data.get('no_of_available')
            # TODO add triggers and transcation shit
            # Update Ward table
            patient_check = f''' select * from viewPatientProfilePatient where patient_id = '{patient_id}';'''
            result = db.execute_dql_commands(patient_check)
            len_check = 0
            for row in result:
                len_check += 1
                print(row[0])
            if len_check == 0:
                return JsonResponse({'status': 'error', 'message': 'There is no patient with this patient_id'},
                                    status=500)
            if result == -1:
                return JsonResponse({'status': 'error', 'message': 'There is no patient with this patient_id'},
                                    status=500)



            patient_gender_check = f''' select gender from viewPatientGenderRec where patient_id = '{patient_id}';'''
            result = db.execute_dql_commands(patient_gender_check)
            patient_gender = 'Male'
            for row in result:
                patient_gender = row[0]
                print(row[0])
            if result == -1:
                return JsonResponse({'status': 'error', 'message': 'There was some error'},
                                    status=500)

            get_ward_gender = f''' select gender from viewWardRec where w_id = {ward_id}'''
            ward_gender = 'Male'
            for row in result:
                ward_gender = row[0]
                print(row[0])
            if ward_gender != patient_gender:
                return JsonResponse({'status': 'error', 'message': 'There was a gender mismatch in patient and ward'},
                                    status=500)
            # Update Inpatient table
            update_inpatient_query = f"BEGIN;\
                                        SELECT assignWardRec('{ward_id}', '{patient_id}');\
                                        COMMIT;"
            checker = db.execute_ddl_and_dml_commands(update_inpatient_query);
            print(checker)
            if checker == -1:
                return JsonResponse({'status': 'error', 'message': 'This ward is currently out of capacity'})

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


@api_view(['POST'])
def edit_profile(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            data = request.data
            rec_id_py = data.get('rec_id')
            gender1 = data['gender']
            if (gender1 != "Male" and gender1 != "Female" and gender1 != "Others"):
                return JsonResponse({'status': 'error', 'message': 'Enter Valid Gender'})
            update_rec_profile_query = f'''
                    SELECT updateRecProfile(
                        '{rec_id_py}',
                        '{data['first_name']}',
                        '{data['last_name']}',
                        '{data['gender']}',
                        '{data['address']}',
                        '{data['nationality']}',
                        '{data['qualification']}',
                        '{data['phoneNumber']}'
                    );
                '''

            # Execute the update query
            db.execute_ddl_and_dml_commands(update_rec_profile_query)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


# receptionist ends here


@api_view(['GET'])
def generateBill(request):
    if request.method == 'GET':
        try:
            patient_id = request.GET.get('p_id')
            # Execute query to fetch all entries from req_appointments table
            query = f"select treat_name , treat_cost from generateBillTreat where patient_id = '{patient_id}';"
            result = db.execute_dql_commands(query)
            time.sleep(0.1)
            print(patient_id)
            # Convert the result to a list of dictionaries
            appointments = []
            count = 0
            cos = []
            for row in result:
                count += 1
                cos.append(row[1])
                appointment = {
                    'treatment_name': row[0],
                    'cost': row[1],
                }
                appointments.append(appointment)
            query = f"""select test_name , test_charge from generateBillTest where patient_id = '{patient_id}';"""
            result = db.execute_dql_commands(query)
            time.sleep(0.1)
            print(patient_id)
            # Convert the result to a list of dictionaries
            tests = []
            count1 = 0
            cost = []
            for row in result:
                count1 += 1
                cost.append(row[1])
                test = {
                    'test_name': row[0],
                    'cost': row[1],
                }
                tests.append(test)
            query = f"select total_payments from paymentPatient where patient_id = '{patient_id}';"
            result = db.execute_dql_commands(query)
            time.sleep(0.1)
            tot = 0
            for row in result:
                tot = row[0]
            print(appointments)
            print(tests)
            return Response({
                'status': 200,
                'treatment': appointments,
                'test': tests,
                'totalTreatmentCost': sum(cos),
                'totalTestCost': sum(cost),
                'totalMedicineCost': tot,
            })
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'Internal server error'
            })


@api_view(['GET'])
def medical_records(request):
    if request.method == 'GET':
        # Get 'from_date' and 'to_date' from the request
        patient_id = request.GET.get('patient_id')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if from_date and to_date is not None:
            if from_date>to_date:
                return JsonResponse({'status': 'error', 'message': 'Enter Valid Dates'})
            try:
                # Execute query to fetch doctor details
                print(to_date)
                print(from_date)
                query = f"""
                        SELECT * FROM getViewPatientRecords1('{patient_id}', 'Confirmed','{from_date}','{to_date}');
                         """
                result = db.execute_dql_commands(query)
                time.sleep(0.01)
                print("Idhar ghusa ki nahi?")
                # print(doctor_id)
                # Check if doctor details are found
                doctor_id = []
                doctor_name = []
                appoint_id = []
                upappointment_details = []
                for row in result:
                    doctor_id.append(row[3])
                    appoint_id.append(row[0])
                    upappointment_detail = {
                        'appointment_id': row[0],
                        'appointment_date': row[1],
                        'appointment_time': row[2],
                        'doctor_id': row[3],
                        'symptoms': row[5],
                        'appointment_status': 'Confirmed',
                        # Add more fields as needed
                    }
                    upappointment_details.append(upappointment_detail)
                # print(upappointment_details,doctor_id,appoint_id)
                for doc_id in doctor_id:
                    query = f"""SELECT * FROM getDoctorNamePatient('{doc_id}');"""
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        doctor_name.append(row[0])
                test_name = []
                treatment_name = []
                disease_name = []
                prescription = []
                for app_id in appoint_id:
                    query = f"""SELECT * FROM labTestPatientFunc('{app_id}');"""
                    t = []
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        t.append(row[0])
                    test_name.append(t)
                    query = f"""SELECT * FROM labTreatPatientFunc('{app_id}');"""
                    treat = []
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        treat.append(row[0])
                    treatment_name.append(treat)
                    query = f"""SELECT * FROM labDiseasePatientFunc('{app_id}');"""
                    d = []
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        d.append(row[0])
                    disease_name.append(d)
                    query = f"""SELECT * FROM labPresPatientFunc('{app_id}');"""
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        prescription.append(row[0])
                # print(doctor_name,test_name,treatment_name,disease_name,prescription)
                return JsonResponse({'status': 'success',
                                     'appointment_details': upappointment_details,
                                     'doctor_name': doctor_name,
                                     'test': test_name,
                                     'treatment': treatment_name,
                                     'disease': disease_name,
                                     'prescription': prescription,
                                     })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Doctor ID parameter missing'}, status=400)


@api_view(['GET'])
def medical_records1(request):
    if request.method == 'GET':
        # Get 'from_date' and 'to_date' from the request
        patient_id = request.GET.get('patient_id')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if from_date and to_date is not None:
            if from_date>to_date:
                return JsonResponse({'status': 'error', 'message': 'Enter Valid Dates'})
            try:
                # Execute query to fetch doctor details
                print(to_date)
                print(from_date)
                query = f"""SELECT * FROM viewUpcomingPatientFunc('{patient_id}', '{from_date}', '{to_date}','Pending');
                         """
                result = db.execute_dql_commands(query)
                time.sleep(0.01)
                print("Idhar ghusa ki nahi?")
                # print(doctor_id)
                # Check if doctor details are found
                doctor_id = []
                doctor_name = []
                appoint_id = []
                upappointment_details = []
                for row in result:
                    doctor_id.append(row[3])
                    appoint_id.append(row[0])
                    upappointment_detail = {
                        'appointment_id': row[0],
                        'appointment_date': row[1],
                        'appointment_time': row[2],
                        'doctor_id': row[3],
                        'symptoms': row[5],
                        'appointment_status': 'Pending',
                        # Add more fields as needed
                    }
                    upappointment_details.append(upappointment_detail)
                # print(upappointment_details,doctor_id,appoint_id)
                for doc_id in doctor_id:
                    query = f"""SELECT * FROM getDoctorNamePatient('{doc_id}');"""
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        doctor_name.append(row[0])

                # print(doctor_name,test_name,treatment_name,disease_name,prescription)
                return JsonResponse({'status': 'success',
                                     'appointment_details': upappointment_details,
                                     'doctor_name': doctor_name,
                                     })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Doctor ID parameter missing'}, status=400)


# patient starts here -----------------------
@api_view(['POST'])
def edit_patient_profile(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            data = request.data
            # get patient_id from login
            # patient_id = 'P001'
            # Initialize list to store SET clauses
            # Construct the UPDATE query
            gender1=data['gender']
            if(gender1!="Male" and gender1!="Female" and gender1!="Others"):
                return JsonResponse({'status': 'error', 'message': 'Enter Valid Gender'})
            weight = int(data['weight'])
            if(weight<0):
                return JsonResponse({'status': 'error', 'message': 'Enter Valid Weight'})
            update_patient_profile_query = f'''
                    SELECT updatePatientProfile(
                    '{data['p_id']}',
                    '{data['first_name']}',
                    '{data['last_name']}',
                    '{data['gender']}',
                    '{int(data['weight'])}',
                    '{data['address']}',
                    '{data['phoneNumber']}'
                );
                '''
            print(update_patient_profile_query)
            # Execute the update query
            db.execute_ddl_and_dml_commands(update_patient_profile_query)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


@api_view(['POST'])
def reqappointment(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            flag = 0
            data = request.data
            symptoms = data['symptoms']
            print(symptoms)
            # get patient_id from login
            # patient_id = 'P001'
            q1 = f"select serial_id from patientRequest where serial_id like 'RQ%';"
            result = db.execute_dql_commands(q1)
            time.sleep(1)
            p_id = []
            new_id = 'RQ001'
            len_result = 0
            for row in result:
                len_result += 1
                p_id.append(row[0])
            print(f'lenresult is {len_result}')
            if len_result == 0:
                new_id = 'RQ001'
            else:
                print("Else me ghusa")
                res = []
                print(len(p_id))
                for i in p_id:
                    i = i.replace(i[0], "", 1)
                    print(type(i))
                    print(i)
                    i = i[2:]
                    i = int(float(i))
                    res.append(i)
                if len(res) == 0:
                    res.append(1)
                    flag = 1
                print(res)
                res.sort(reverse=True)
                if flag == 0:
                    new_id = res[0] + 1
                new_id = 'RQ' + f'{new_id:03d}'
            print(f'new_id is {new_id}')
            print(symptoms)
            # Construct the UPDATE query  #pass patient id from webpage, receptionist_id remove,
            request_app_query = f''' 
                    SELECT patientRequestFunc('{new_id}', '{data['p_id']}', 'R001', '{symptoms}', LOCALTIMESTAMP);  
                '''
            print(request_app_query)
            # Execute the update query
            db.execute_ddl_and_dml_commands(request_app_query)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


@api_view(['GET'])
def viewmyreq(request):
    if request.method == 'GET':
        try:
            # Execute query to fetch all entries from req_appointments table
            patient_id = request.GET.get('patient_id')  # HARDCODED, CHANGE @RACHIT
            query = f"select * from viewAppointmentReqPatient('{patient_id}');"
            result = db.execute_dql_commands(query)
            print("CHut marale")
            # Convert the result to a list of dictionaries
            appointments = []
            for row in result:
                appointment = {
                    'serial_id': row[0],
                    'patient_id': row[1],
                    'rec_id': row[2],
                    'symptoms': row[3],
                    't_stamp': row[4],

                    # Add more fields as needed
                }
                appointments.append(appointment)
            print(appointments)
            return Response({
                'status': 200,
                'appointments': appointments
            })
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'Internal server error'
            })


# patient ends here -------------------------


# daktor starts here

@api_view(['GET'])
def appointment_range(request):
    if request.method == 'GET':
        # Get 'from_date' and 'to_date' from the request
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        doctor_id = request.GET.get('doctor_id')
        if from_date and to_date is not None:
            try:
                # Execute query to fetch doctor details
                print(to_date)
                print(from_date)
                if to_date < from_date:
                    return JsonResponse({'status': 'error', 'message': 'Enter Valid date range'})
            #     CREATE
            #     OR
            #     REPLACE
            #     FUNCTION
            #     get_doctor_appointments(
            #         fromd
            #     DATE,
            #     tod
            #     DATE
            #     )
            #     RETURNS
            #     TABLE(
            #         appointment_id_new
            #     VARCHAR,
            #     appointment_date_new
            #     DATE,
            #     appointment_time_new
            #     TIME,
            #     doctor_id_new
            #     VARCHAR,
            #     symptoms_new
            #     VARCHAR
            #     ) AS $$
            #     BEGIN
            #     RETURN
            #     QUERY
            #     SELECT
            #     appointment_id, appointment_date, appointment_time, doctor_id, symptoms
            #     FROM
            #     appointment_schedule
            #     WHERE
            #     appointment_date
            #     BETWEEN
            #     fromd
            #     AND
            #     tod
            #     AND
            #     doctor_id = '{doctor_id}'
            #     ORDER
            #     BY
            #     appointment_date
            #     ASC;
            # END;
            # $$ LANGUAGE
            # plpgsql;
                query = f'''
                

                SELECT * FROM get_doctor_appointments('{from_date}', '{to_date}');

                '''
                result = db.execute_dql_commands(query)
                time.sleep(0.01)
                print("Idhar ghusa ki nahi?")
                # print(doctor_id)
                # Check if doctor details are found
                appointment_details = []
                for row in result:
                    appointment_detail = {
                        'appointment_id': row[0],
                        'appointment_date': row[1],
                        'appointment_time': row[2],
                        'symptoms': row[4],
                        # Add more fields as needed
                    }
                    appointment_details.append(appointment_detail)
                print(appointment_details)
                return JsonResponse({'status': 'success', 'appointment_details': appointment_details})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Doctor ID parameter missing'}, status=400)


@api_view(['GET'])
def patient_records(request):
    if request.method == 'GET':
        # Get 'from_date' and 'to_date' from the request
        patient_id = request.GET.get('patient_id')

        if patient_id is not None:
            try:
                # Execute query to fetch doctor details

                query = f"""SELECT *  
                        FROM appointment_schedule 
                        WHERE patient_id = '{patient_id}'
                        and appointment_status = 'Confirmed'
                        ORDER BY appointment_date ASC; """
                result = db.execute_dql_commands(query)
                time.sleep(0.01)
                print("Idhar ghusa ki nahi?")
                # print(doctor_id)
                # Check if doctor details are found
                doctor_id = []
                doctor_name = []
                appoint_id = []
                upappointment_details = []
                for row in result:
                    doctor_id.append(row[3])
                    appoint_id.append(row[0])
                    upappointment_detail = {
                        'appointment_id': row[0],
                        'appointment_date': row[1],
                        'appointment_time': row[2],
                        'doctor_id': row[3],
                        'symptoms': row[5],
                        'appointment_status': 'Closed',
                        # Add more fields as needed
                    }
                    upappointment_details.append(upappointment_detail)
                # print(upappointment_details,doctor_id,appoint_id)
                for doc_id in doctor_id:
                    query = f"""SELECT * FROM getDoctorNamePatient('{doc_id}');"""
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        doctor_name.append(row[0])
                test_name = []
                treatment_name = []
                disease_name = []
                prescription = []
                for app_id in appoint_id:
                    query = f"""SELECT * FROM labTestPatientFunc('{app_id}');"""
                    t = []
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        t.append(row[0])
                    test_name.append(t)
                    query = f"""SELECT * FROM labTreatPatientFunc('{app_id}');"""
                    treat = []
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        treat.append(row[0])
                    treatment_name.append(treat)
                    query = f"""SELECT * FROM labDiseasePatientFunc('{app_id}');"""
                    d = []
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        d.append(row[0])
                    disease_name.append(d)
                    query = f"""SELECT * FROM labPresPatientFunc('{app_id}');"""
                    result = db.execute_dql_commands(query)
                    time.sleep(0.01)
                    for row in result:
                        prescription.append(row[0])
                # print(doctor_name,test_name,treatment_name,disease_name,prescription)
                return JsonResponse({'status': 'success',
                                     'appointment_details': upappointment_details,
                                     'doctor_name': doctor_name,
                                     'test': test_name,
                                     'treatment': treatment_name,
                                     'disease': disease_name,
                                     'prescription': prescription,
                                     })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Doctor ID parameter missing'}, status=400)


@api_view(['POST'])
def prescription_update(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            print(data)
            # Extract appointment details from the data
            appointment_id = data.get('appointment_id')
            disease = data.get('d_name')
            prescription = data.get('prescription')
            doctor_id = data.get('doctor_id')

            print(appointment_id)
            # Define the SQL statement to check if appointment is pending
            check_appointment_sql = f"""
                SELECT appointment_status FROM appointment_schedule_view2 
                WHERE appointment_id='{appointment_id}' AND appointment_status='Pending' AND doctor_id='{data['doctor_id']}'
            """
            # Execute the SQL statement to check appointment status
            result0 = db.execute_dql_commands(check_appointment_sql)
            try:
                # Iterate over the result to extract appointment status
                for row in result0:
                    resid0 = row[0]
            except IndexError:
                # Handle IndexError, meaning no rows were returned
                return JsonResponse({'status': 'error', 'message': 'Appointment is already closed or does not exist'},
                                    status=400)

            if not resid0:
                return JsonResponse({'status': 'error', 'message': 'Appointment is already closed or does not exist'},
                                    status=400)

            print(appointment_id)
            # Convert appointment_date and appointment_time to datetime objects
            print("Nanga naach")
            # Define the SQL statement to insert into appointment_schedule table
            get_did = f"""
                select d_id from disease_type where d_name='{disease}'
            """
            result = db.execute_dql_commands(get_did)
            print(result)
            if result:
                print(result)
            else:
                return JsonResponse({'status': 'error', 'message': ' blah'},
                                    status=400)
            for row in result:
                resid = row[0]


            print(resid)
            sql_insert = f"""
                INSERT INTO examine (examine_id, appointment_id, d_id, prescription)
                    SELECT 
                    'E' || LPAD((SUBSTRING(MAX(examine_id) FROM 2)::INTEGER + 1)::TEXT, 3, '0'), 
                    '{appointment_id}', 
                    '{resid}', 
                    '{prescription}'
                FROM examine;

            """

            # Execute the SQL statement with parameters using db.execute_ddl_and_dml_commands
            db.execute_ddl_and_dml_commands(sql_insert)
            time.sleep(1)
            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Prescription created successfully'})
        except Exception as e:
            # Return an error response if there's an exception
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        # Return an error response for unsupported request methods
        return JsonResponse({'status': 'error', 'message': 'Unsupported request method'}, status=405)


@api_view(['POST'])
def treatment_update(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            print(data)
            # Extract appointment details from the data
            appointment_id = data.get('appointment_id')
            disease = data.get('d_name')
            treatment = data.get('treat_name')
            enddate = data.get('end_date')
            doctor_id = data.get('doctor_id')

            print(treatment)
            check_appointment_sql = f"""
                SELECT appointment_status FROM appointment_schedule
                WHERE appointment_id='{appointment_id}' AND appointment_status='Pending' AND doctor_id= '{data['doctor_id']}';
            """
            # Execute the SQL statement to check appointment status
            result0 = db.execute_dql_commands(check_appointment_sql)
            try:
                # Iterate over the result to extract appointment status
                for row in result0:
                    resid0 = row[0]
            except IndexError:
                # Handle IndexError, meaning no rows were returned
                return JsonResponse({'status': 'error', 'message': 'Appointment is already closed or does not exist'},
                                    status=400)

            if not resid0:
                return JsonResponse({'status': 'error', 'message': 'Appointment is already closed or does not exist'},
                                    status=400)
            # Convert appointment_date and appointment_time to datetime objects

            # Define the SQL statement to insert into appointment_schedule table
            get_did = f"""
                select d_id from disease_type where d_name='{disease}'
            """
            result = db.execute_dql_commands(get_did)

            for row in result:
                resid = row[0]

            print(resid)
            get_tid = f"""
                select treat_id from treatment_view where treat_name='{treatment}'
            """
            result2 = db.execute_dql_commands(get_tid)

            for row in result2:
                resid2 = row[0]

            print(resid2)
            print(appointment_id)
            get_sid = f"""
                select appointment_date from appointment_schedule_view_date where appointment_id='{appointment_id}'
            """
            result3 = db.execute_dql_commands(get_sid)

            for row in result3:
                resid3 = row[0]

            print(resid3)
            sql_insert = f"""
                INSERT INTO patient_treatment (pt_id, st_date, end_Date, treat_id, d_id, appointment_id)
                SELECT 
                    'PT' || LPAD((SUBSTRING(MAX(pt_id) FROM 3)::INTEGER + 1)::TEXT, 3, '0'), 
                    '{resid3}', 
                    '{enddate}', 
                    '{resid2}',
                    '{resid}', 
                    '{appointment_id}'
                FROM patient_treatment;

            """

            # Execute the SQL statement with parameters using db.execute_ddl_and_dml_commands
            db.execute_ddl_and_dml_commands(sql_insert)
            time.sleep(1)
            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Treatment created successfully'})
        except Exception as e:
            # Return an error response if there's an exception
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        # Return an error response for unsupported request methods
        return JsonResponse({'status': 'error', 'message': 'Unsupported request method'}, status=405)


@api_view(['POST'])
def test_update(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            print(data)
            # Extract appointment details from the data
            appointment_id = data.get('appointment_id')
            test = data.get('test_name')
            doctor_id = data.get('doctor_id')

            check_appointment_sql = f"""
                SELECT appointment_status FROM appointment_schedule
                WHERE appointment_id='{appointment_id}' AND appointment_status='Pending' AND doctor_id='{data['doctor_id']}'
            """
            # Execute the SQL statement to check appointment status
            result0 = db.execute_dql_commands(check_appointment_sql)
            try:
                # Iterate over the result to extract appointment status
                for row in result0:
                    resid0 = row[0]
            except IndexError:
                # Handle IndexError, meaning no rows were returned
                return JsonResponse({'status': 'error', 'message': 'Appointment is already closed or does not exist'},
                                    status=400)

            if not resid0:
                return JsonResponse({'status': 'error', 'message': 'Appointment is already closed or does not exist'},
                                    status=400)

            # Convert appointment_date and appointment_time to datetime objects

            # Define the SQL statement to insert into appointment_schedule table
            get_ltid = f"""
                select lt_id from laboratory where test_name='{test}'
            """
            result = db.execute_dql_commands(get_ltid)

            for row in result:
                resid = row[0]

            print(resid)

            sql_insert = f"""
                INSERT INTO test (test_id, lt_id, appointment_id)
                SELECT 
                    'T' || LPAD((SUBSTRING(MAX(test_id) FROM 2)::INTEGER + 1)::TEXT, 3, '0'), 
                    '{resid}', 
                    '{appointment_id}'
                FROM test;

            """

            # Execute the SQL statement with parameters using db.execute_ddl_and_dml_commands
            db.execute_ddl_and_dml_commands(sql_insert)
            time.sleep(1)
            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Test created successfully'})
        except Exception as e:
            # Return an error response if there's an exception
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        # Return an error response for unsupported request methods
        return JsonResponse({'status': 'error', 'message': 'Unsupported request method'}, status=405)


@api_view(['POST'])
def close(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            appointment_id = data.get('appointment_id')

            sql_update = f"""

                SELECT update_appointment_status('{appointment_id}');
            """

            # Execute the SQL statement with parameters using db.execute_ddl_and_dml_commands
            db.execute_ddl_and_dml_commands(sql_update)
            time.sleep(1)
            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Lab Test Prescribed successfully'})
        except Exception as e:
            # Return an error response if there's an exception
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        # Return an error response for unsupported request methods
        return JsonResponse({'status': 'error', 'message': 'Unsupported request method'}, status=405)


@api_view(['POST'])
def edit_doctor_profile(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            data = request.data
            # get patient_id from login
            # patient_id = 'P001'
            # Initialize list to store SET clauses
            set_clauses = []
            set_clauses_user = []
            # Check if each field is provided and add it to the SET clause
            if data['gender'] != "Male" and data['gender'] != "Female" and data['gender'] != "Others":
                return JsonResponse({'status': 'error', 'message': 'Enter Valid gender'})
            if data['first_name'] != "":
                set_clauses.append(f"fname = COALESCE('{data['first_name']}', fname)")
                set_clauses_user.append(f"fname = COALESCE('{data['first_name']}', fname)")
            if data['last_name'] != "":
                set_clauses.append(f"lname = COALESCE('{data['last_name']}', lname)")
                set_clauses_user.append(f"lname = COALESCE('{data['last_name']}', lname)")
            if data['gender'] != "":
                set_clauses.append(f"gender = COALESCE('{data['gender']}', gender)")
                set_clauses_user.append(f"gender = COALESCE('{data['gender']}', gender)")
            if data['address'] != "":
                set_clauses.append(f"address = COALESCE('{data['address']}', address)")
            if data['phoneNumber'] != "":
                set_clauses.append(f"phone_no = COALESCE('{data['phoneNumber']}', phone_no)")
                set_clauses_user.append(f"phone_no = COALESCE('{data['phoneNumber']}', phone_no)")

            # Construct the SET clause string
            set_clause_str = ', '.join(set_clauses)
            set_clause_str_user = ', '.join(set_clauses_user)

            sql_trigger = f'''
            -- Create the trigger function
            CREATE OR REPLACE FUNCTION update_user_table_on_doctor_update8()
            RETURNS TRIGGER AS
            $$
            BEGIN
                -- Update the corresponding row in the user_table
                UPDATE user_table_view
                SET 
                    {set_clause_str_user}
                WHERE
                    user_id = '{data['doctor_id']}';

                RETURN NEW;
            END;
            $$
            LANGUAGE plpgsql;

            -- Create the trigger
            CREATE OR REPLACE TRIGGER trigger_update_user_table_on_doctor_update8
            AFTER UPDATE ON doctor
            FOR EACH ROW
            EXECUTE FUNCTION update_user_table_on_doctor_update8();


            '''
            db.execute_ddl_and_dml_commands(sql_trigger)
            time.sleep(1)

            # Construct the UPDATE query
            update_doctor_profile_query = f'''
                    UPDATE doctor_view
                    SET {set_clause_str}
                    WHERE doctor_id = '{data['doctor_id']}';

                '''
            print(update_doctor_profile_query)
            # Execute the update query
            db.execute_ddl_and_dml_commands(update_doctor_profile_query)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


# doctor ends here

# Staff Starts
@api_view(['GET'])
def view_prescriptions(request):
    if request.method == 'GET':
        patient_id = request.GET.get('patient_id')
        # data = request.data
        print(patient_id)
        # print(data)
        # patient_id = data['patientId']
        if patient_id:
            query = f'''
               select * from viewpres where patient_id='{patient_id}';
            '''
            result = db.execute_dql_commands(query)
            prescription_data = []
            for row in result:
                # print("gay")
                prescription_data.append({
                    'patient_id': row[0],
                    'appointment_id': row[1],
                    'prescription': row[2]
                })
            print("lenght")
            print(len(prescription_data))
            if len(prescription_data) < 1 :
                return JsonResponse({'status': 'error', 'message': 'Patient not found'})

            return JsonResponse({'status': 'success', 'prescriptions': prescription_data})
        else:
            return JsonResponse({'status': 'error', 'message': 'Patient ID is required'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'})


# View for selling medicine
@api_view(['POST'])
def sell_medicine(request):
    if request.method == 'POST':
        data = request.data
        medicine_name1 = data.get('medicine_name')

        quantity1 = data.get('quantity')
        if(quantity1==""):
            return JsonResponse({'status': 'error', 'message': 'Enter Quantity Please'})
        quantity=int(quantity1)
        if(quantity<0):
            return JsonResponse({'status': 'error', 'message': 'Enter Valid Quantity '})

        # sale_price = int(data.get('sale_price'))
        customer_name = data.get('customer_name')

        query = f'''
                    SELECT available_quantity FROM sellrestock_medstore WHERE medicine_name = '{medicine_name1}';  
                '''
        print("check")
        # db.execute_ddl_and_dml_commands(quer)
        result = db.execute_dql_commands(query)
        available_quantity = 0
        dic1 = []
        for row in result:
            dic1.append(row[0])
        if (len(dic1) == 0):
            return JsonResponse({'status': 'error', 'message': 'Invalid Medicine Name'})
        else:
            available_quantity = int(row[0])

        print(available_quantity)

        print("check1")
        query2 = f"SELECT total_payments FROM sell_Inpatient WHERE patient_id = '{customer_name}'"

        res1 = db.execute_dql_commands(query2)
        dic2 = []
        for row in res1:
            dic2.append(row[0])
        if (len(dic2) == 0):
            return JsonResponse({'status': 'error', 'message': 'Invalid Patient Name'})
        else:
            print(row[0])

        if available_quantity >= quantity:

            query = f'''
                    CREATE OR REPLACE function UpdateInpatientPayments1()
                    returns trigger
                    language plpgsql
                    AS $$
                    BEGIN
                        UPDATE sell_Inpatient
                        SET total_payments = total_payments + ('{quantity}' * (SELECT medicine_price FROM sellrestock_medstore WHERE medicine_name = '{medicine_name1}'))
                        WHERE patient_id = '{customer_name}';
                        return new;
                    END;
                    $$;

                  CREATE or replace TRIGGER AfterMedicineUpdate
                  AFTER UPDATE ON medicalstore
                  FOR EACH ROW execute function UpdateInpatientPayments1();

                '''
            query1 = f"call sell_medicine_procedure('{medicine_name1}', '{quantity}');"

            #db.execute_ddl_and_dml_commands(query)
            db.execute_ddl_and_dml_commands(query1)

            print("check2")

            # Perform sale operations here

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Insufficient quantity in stock'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


# View for restocking medicine
@api_view(['POST'])
def restock_medicine(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        medicine_name1 = data['medicine_name']
        # print(medicine_name + "heehehe")
        quantity1 = data.get('quantity')
        if (quantity1 == ""):
            return JsonResponse({'status': 'error', 'message': 'Enter Quantity Please'})
        quantity = int(quantity1)
        if (quantity < 0):
            return JsonResponse({'status': 'error', 'message': 'Enter Valid Quantity '})
        # print(quantity + "heehehe")
        cost_price1 = data['cost_price']
        if (cost_price1 == ""):
            return JsonResponse({'status': 'error', 'message': 'Enter Cost of Medicine Please'})
        cost_price=int(cost_price1)
        if (cost_price < 0):
            return JsonResponse({'status': 'error', 'message': 'Enter Valid Price '})



        query = f''' 
                    call update_medstore('{medicine_name1}','{quantity}','{cost_price}');
                '''
        db.execute_ddl_and_dml_commands(query)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


# View for updating profile
@api_view(['POST'])
def edit_profile_staff(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        print("eheehee")
        user_id = data.get('staff_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        gender1 = data.get('gender')
        if(gender1!="Male" and gender1!="Female" and gender1!="Others" ):
            return JsonResponse({'status': 'error', 'message': 'Enter Valid gender'})
        phone_no1 = data.get('phone_no')

        query = f'''update staff_user_table set
                fname = COALESCE(NULLIF('{first_name}', ''), fname),
                lname = COALESCE(NULLIF('{last_name}', ''), lname),
                gender = COALESCE(NULLIF('{gender1}', ''), gender),
                phone_no = COALESCE(NULLIF('{phone_no1}', ''), phone_no)
                where user_id='{user_id}';
                '''
        db.execute_ddl_and_dml_commands(query)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


# discuss about view prescription, restock
# and change in sell medicine
# Staff Ends

# Admin Starts
@api_view(['POST'])
def add_user(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        print("eheehee")
        user_id = ''
        u_password = data.get('u_password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        gender1 = data.get('gender')
        if (gender1 != "Male" and gender1 != "Female" and gender1 != "Others"):
            return JsonResponse({'status': 'error', 'message': 'Enter Valid gender'})
        phone_no1 = data.get('phone_no')
        role = data.get('role')
        g = role[0].upper()

        q1 = f"select user_id from user_table where user_id like '{g}%';"
        result = db.execute_dql_commands(q1)
        time.sleep(1)
        p_id = []
        for row in result:
            p_id.append(row[0])
        if (len(p_id) == 0):
            print("gay")
            user_id = g + '001'
        else:
            res = []
            for i in p_id:
                i = i.replace(i[0], "", 1)
                i = int(i)
                res.append(i)
            print(res)
            res.sort(reverse=True)
            user_id = res[0] + 1
            user_id = g + f'{user_id:03d}'

        query = f'''DO $$
                    declare
                    begin
                    insert into user_table (user_id,u_password,fname,lname,gender,phone_no)
                    values
                    ('{user_id}','{u_password}','{first_name}','{last_name}','{gender1}','{phone_no1}');
                    drop user if exists {user_id};
                    create user {user_id} WITH PASSWORD 'postgres';

                    GRANT {role} TO {user_id};
                    if('{role}'='doctor') then 
                    insert into doctor (doctor_id,fname,lname,gender,phone_no)
                    values
                    ('{user_id}','{first_name}','{last_name}','{gender1}','{phone_no1}');


                    elsif('{role}'='receptionist') then 
                    insert into receptionist (rec_id,fname,lname,gender,phone_no)
                    values
                    ('{user_id}','{first_name}','{last_name}','{gender1}','{phone_no1}');

                    elsif('{role}'='patient') then 
                    insert into Inpatient (patient_id,fname,lname,gender,phone_no)
                    values
                    ('{user_id}','{first_name}','{last_name}','{gender1}','{phone_no1}');
                    end if;
                    end$$;

                '''
        db.execute_ddl_and_dml_commands(query)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


@api_view(['POST'])
def update_user(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        print("eheehee")
        user_id = data.get('user_id')
        u_password1 = data.get('u_password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        gender1 = data.get('gender')
        if (gender1 != "Male" and gender1 != "Female" and gender1 != "Others"):
            return JsonResponse({'status': 'error', 'message': 'Enter Valid gender'})
        phone_no1 = data.get('phone_no')
        role = data.get('role')
        if (user_id[0] != role[0].upper()):
            return JsonResponse({'status': 'error', 'message': 'Id and role do not match'})
        else:

            query = f'''DO $$
                        declare
                        begin
                        update user_table set
                        u_password=COALESCE(NULLIF('{u_password1}', ''), u_password),
                        fname = COALESCE(NULLIF('{first_name}', ''), fname),
                        lname = COALESCE(NULLIF('{last_name}', ''), lname),
                        gender = COALESCE(NULLIF('{gender1}', ''), gender),
                        phone_no = COALESCE(NULLIF('{phone_no1}', ''), phone_no)
                        where user_id='{user_id}';
                        if('{role}'='doctor') then 
                        update doctor set
                        fname = COALESCE(NULLIF('{first_name}', ''), fname),
                        lname = COALESCE(NULLIF('{last_name}', ''), lname),
                        gender = COALESCE(NULLIF('{gender1}', ''), gender),
                        phone_no = COALESCE(NULLIF('{phone_no1}', ''), phone_no)
                        where doctor_id='{user_id}';

                        elsif('{role}'='receptionist') then 
                        update receptionist set
                        fname = COALESCE(NULLIF('{first_name}', ''), fname),
                        lname = COALESCE(NULLIF('{last_name}', ''), lname),
                        gender = COALESCE(NULLIF('{gender1}', ''), gender),
                        phone_no = COALESCE(NULLIF('{phone_no1}', ''), phone_no)
                        where rec_id='{user_id}';

                        elsif('{role}'='patient') then 
                        update inpatient set
                        fname = COALESCE(NULLIF('{first_name}', ''), fname),
                        lname = COALESCE(NULLIF('{last_name}', ''), lname),
                        gender = COALESCE(NULLIF('{gender1}', ''), gender),
                        phone_no = COALESCE(NULLIF('{phone_no1}', ''), phone_no)
                        where patient_id='{user_id}';
                        end if;
                        end$$;

                    '''
            db.execute_ddl_and_dml_commands(query)
            return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


@api_view(['POST'])
def delete_user(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        print("eheehee")
        user_id = data.get('user_id')
        role = data.get('role')
        if (user_id[0] != role[0].upper()):
            return JsonResponse({'status': 'error', 'message': 'Id and role do not match'})
        else:
            query = f'''DO $$
                        declare
                        begin
                        delete from user_table 
                        where user_id='{user_id}';

                        if('{role}'='doctor') then 
                        delete from doctor
                        where doctor_id='{user_id}';

                        elsif('{role}'='receptionist') then 
                        delete from  receptionist 
                        where rec_id='{user_id}';

                        elsif('{role}'='patient') then 
                        delete from inpatient
                        where patient_id='{user_id}';
                        end if;
                        end$$;

                    '''
            db.execute_ddl_and_dml_commands(query)
            return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


@api_view(['POST'])
def edit_profile_admin(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        print("eheehee")
        user_id = data.get('admin_id')
        admin_pass = data.get('admin_pass')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        gender1 = data.get('gender')
        if (gender1 != "Male" and gender1 != "Female" and gender1 != "Others"):
            return JsonResponse({'status': 'error', 'message': 'Enter Valid gender'})
        address1 = data.get('address')
        phone_no1 = data.get('phone_no')

        query = f'''update system_administrator set
                a_password=COALESCE(NULLIF('{admin_pass}', ''),a_password ),
                fname = COALESCE(NULLIF('{first_name}', ''), fname),
                lname = COALESCE(NULLIF('{last_name}', ''), lname),
                gender = COALESCE(NULLIF('{gender1}', ''), gender),
                address = COALESCE(NULLIF('{address1}', ''), address),
                phone_no = COALESCE(NULLIF('{phone_no1}', ''), phone_no)
                where admin_id='{user_id}';
                '''
        db.execute_ddl_and_dml_commands(query)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})

@api_view(['POST'])
def view_app(request):
    if request.method == 'POST':
        data = request.data
        print("ghusa")
        st_date = data.get('startDate')
        end_date=data.get('endDate')
        # data = request.data
        #print(patient_id)
        # print(data)
        # patient_id = data['patientId']
        if (st_date and end_date ):
            query = f'''
               select * from appointment_schedule where appointment_date between '{st_date}' and '{end_date}';
            '''
            result = db.execute_dql_commands(query)
            prescription_data = []
            for row in result:
                # print("gay")
                prescription_data.append({
                    'appointmentid': row[0],
                    'appointmentdate': row[1],
                    'appointmenttime': row[2],
                    'doctorid': row[3],
                    'patientid': row[4],
                    'symptoms': row[5],
                    'appointmentstatus': row[6],
                })
            #print(prescription_data)
            if (len(prescription_data) == 0):
                return JsonResponse({'status': 'error', 'message': 'Patient not found'})

            return JsonResponse({'status': 'success', 'appointments': prescription_data})
        else:
            return JsonResponse({'status': 'error', 'message': 'Patient ID is required'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'})




# Admin Ends

