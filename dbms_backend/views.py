from django.shortcuts import render


def loginPage(request):
    return render(request, 'login_page/index.html')

def homePage(request):
    return render(request, 'home_page/home.html')

def patientPage(request):
    return render(request, 'patient_page/patient.html')

def signupPage(request):
    return render(request, 'signup_page/signup.html')

def receptionistPage(request):
    return render(request, 'receptionist_page/receptionist.html')

def staffPage(request):
    return render(request, 'staff_page/staff.html')

def adminPage(request):
    return render(request,'admin_page/admin.html')