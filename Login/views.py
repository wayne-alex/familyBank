import calendar
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from _decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import SignUpForm, EditUserForm, ContributionForm
from .models import *


def send_message(message):
    url = 'http://16.171.134.101:3000/send-message'
    message_content = message

    # Create a dictionary with the message content
    payload = {'message': message_content}

    try:
        response = requests.post(url, json=payload)

        # Check the response status code
        if response.status_code == 200:
            print("Request successful!")
            print("Server response:", response.text)
        else:
            print(f"Request failed with status code {response.status_code}")
            print("Server response:", response.text)

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


# Create your views here.

def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            admin = Account.objects.get(name=username)
            if not admin.status:
                messages.success(request, "Your account is disabled or not verified by Admin.Contact Admin")
                logout(request)
                return redirect('home')
            else:
                messages.success(request, "You have successfully signed in")
                activity_log = ActivityLog(user=request.user.username, action='Logging in',
                                           details='User Logged in into there account')
                activity_log.save()

                return redirect('dashboard')
        else:
            messages.error(request, "There was an error while signing in")
            return redirect('home')
    else:
        return render(request, 'home.html')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Information saved successfully! Welcome to Family Bank")
            activity_log = ActivityLog(user=request.user, action='Account creation',
                                       details='User created Family Bank account')
            activity_log.save()

            acc_ = Account(user_id=request.user.id, name=request.user.username)
            acc_.save()
            monthly = MonthlyActivity(member=request.user.username)
            monthly.save()
            number = Account.objects.all().count() + 1

            turn = Turn(member=request.user.username, number=number)
            turn.save()

            message = (
                "Dear {},\n\n"
                "We're thrilled to have you as a part of our financial family. As a member of Family Bank, you'll have access to a wide range of banking services designed to help you achieve your financial goals.\n\n"
                "Whether you're saving for the future, planning a big purchase, or looking for convenient ways to manage your finances, we're here to support you every step of the way.\n\n"
                "If you have any questions or need assistance, our dedicated support team is always ready to help. Feel free to reach out to us through our website, phone, or visit one of our branches near you.\n\n"
                "Thank you for choosing Family Bank for your banking needs. We're excited to embark on this financial journey together.\n\n"
                "Best regards,\n\n"
                "~The Family Bank Team"
            )
            formatted_message = message.format(request.user.username)

            message_welcome = Notification(type='team', username=request.user.username, sender='Family Bank Team',
                                           message=formatted_message)
            message_welcome.save()
            send_message(formatted_message)

            admin = Account.objects.get(name=request.user.username)
            if not admin.status:
                messages.success(request, "Your account is disabled or not verified by Admin.Contact Admin")
                logout(request)
                return redirect('home')
            else:
                return redirect('dashboard')


    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})


def forgot_password(request):
    pass


def verify_phone_number(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        url = 'http://13.51.196.90:3000/trigger-function'
        payload = {'phone_number': phone}
        user_id = request.user.id
        verified = False

        # Check if the phone number is already associated with another user
        try:
            account = Account.objects.get(phone_number=phone)
            if account.user_id != user_id:
                messages.error(request,
                               'The phone number is already in use by another user. Please try another number.')
                return render(request, 'mobile.html', {'verification_code_sent': False})
        except Account.DoesNotExist:
            # If the phone number is not associated with any user, create a new account
            account = Account.objects.get(user_id=request.user.id)
            account.phone_number = phone
            account.save()

        # If the phone number is associated with the current user or not associated with any user, continue with
        # sending the verification code
        try:
            response = requests.get(url, params=payload)
            response.raise_for_status()
            code = response.text.replace('Message successfully sent. Verification code is: ', '')

            # Store the code in the session
            request.session['verification_code'] = code

            return render(request, 'mobile.html', {'verification_code_sent': True})

        except requests.exceptions.RequestException as e:
            messages.error(request, 'Error while sending the verification code.')
            print(f"Error: {e}")
            return render(request, 'mobile.html', {'verification_code_sent': False})

    else:
        return render(request, 'mobile.html', {'verification_code_sent': False})


def verify_code(request):
    if request.method == 'POST':
        # Retrieve the code from the session
        code = request.session.get('verification_code', None)
        if not code:
            # Handle the case where the code is not found in the session
            # Redirect or show an error message, etc.
            return redirect('verify_phone_number')

        # Process the code and check if it matches the user input.
        user_input_code = request.POST.get('verification_code')
        if code == user_input_code:
            messages.success(request, "Phone number successfully Verified")
            account = Account.objects.get(user_id=request.user.id)
            account.verified = True
            account.save()
            return render(request, 'dashboard.html')  # Replace 'success_page' with the URL of the success page.
        else:
            # Code is incorrect, display an error message, or redirect back to the verification page.
            messages.success(request, "Verification code entered is incorrect.")
            logout(request)
            return redirect('phone_verification')

    else:
        return redirect('verify_phone_number')


def resend_code(request):
    # Code to resend the verification code goes here.
    return redirect('verify_phone_number')


def change_number(request):
    # Code to allow the user to change their phone number goes here.
    return redirect('verify_phone_number')


def dashboard(request):
    loan = Loan.objects.get(id=1)
    acc_ = Account.objects.get(user_id=request.user.id)
    monthly = MonthlyActivity.objects.get(member=request.user.username)
    turn = Turn.objects.get(member=request.user.username)
    notification = Notification.objects.filter(username=request.user.username).order_by('-id')[:3]
    return render(request, 'dashboard.html',
                  {'loan': loan, 'account': acc_, 'monthly': monthly, 'turn': turn, 'notification': notification})


def loans(request):
    if request.method == 'POST':
        loan_amount = request.POST['loan']
        activity_log = ActivityLog(user=request.user, action='Loan Application',
                                   details='User applied for a loan KES' + loan_amount)
        activity_log.save()

        amount = int(loan_amount)
        loan_limit = Loan.objects.get(id=1)
        _loan_limit = int(loan_limit.loan)
        if amount > _loan_limit:
            messages.success(request, 'Loan Amount cant be more than Total Loan Available')
            return redirect('loans')
        else:
            member = request.user.username
            interest = 10
            current_date = datetime.now().date()
            date_due = current_date + timedelta(days=30)
            apply = Apply(member=member, amount=amount, interest_rate=interest, date_due=date_due, type=0,
                          status='pending')
            apply.save()
            _loan = Loan.objects.get(id=1)
            _loan.loan = _loan.loan - amount
            _loan.save()
            messages.success(request, 'Loan Application Successful wait for Admin to confirm')
            formatted_message = f"Dear {member},\n\n Your Loan application is received awaiting Admin confirmation" \
                                "\n\nRegards, \n~Family Bank Team."
            send_message(formatted_message)
            return redirect('loans')

    else:
        loan = Loan.objects.get(id=1)
        acc_ = Account.objects.get(user_id=request.user.id)
        monthly = MonthlyActivity.objects.get(member=request.user.username)
        turn = Turn.objects.get(member=request.user.username)
        apply = Apply.objects.filter(member=request.user.username, type=0).first()
        notification = Notification.objects.filter(username=request.user.username).order_by('-id')[:3]
        total_amount = None

        if apply:
            total_amount = apply.amount + (apply.amount * (apply.interest_rate / 100))

        return render(request, 'loan.html',
                      {'loan': loan, 'account': acc_, 'monthly': monthly, 'turn': turn, 'loan_balance': total_amount,
                       'apply': apply, 'notification': notification})


def transactions(request):
    loan = Loan.objects.get(id=1)
    acc_ = Account.objects.get(user_id=request.user.id)
    monthly = MonthlyActivity.objects.get(member=request.user.username)
    turn = Turn.objects.get(member=request.user.username)
    applies = Apply.objects.filter(member=request.user.username).order_by('-id')
    notification = Notification.objects.filter(username=request.user.username).order_by('-id')[:3]
    return render(request, 'transactions.html',
                  {'loan': loan, 'account': acc_, 'monthly': monthly, 'turn': turn, 'apply': applies,
                   'notification': notification})


def logs(request):
    loan = Loan.objects.get(id=1)
    acc_ = Account.objects.get(user_id=request.user.id)
    monthly = MonthlyActivity.objects.get(member=request.user.username)
    turn = Turn.objects.get(member=request.user.username)
    applies = Apply.objects.filter(member=request.user.username).order_by('-id')
    logs = ActivityLog.objects.filter(user=request.user.username).order_by('-id')
    notification = Notification.objects.filter(username=request.user.username).order_by('-id')[:3]
    return render(request, 'activityLog.html',
                  {'loan': loan, 'account': acc_, 'monthly': monthly, 'turn': turn, 'apply': applies, 'logs': logs,
                   'notification': notification})


def logout_user(request):
    messages.success(request, "You have been logged out")
    activity_log = ActivityLog(user=request.user.username, action='Logging out',
                               details='User Logged out of there account')
    activity_log.save()
    logout(request)
    return redirect('home')


def notification(request, sender, id):
    _notify = Notification.objects.get(id=id)
    _notify.read = 1
    _notify.save()
    notify = Notification.objects.filter(sender=sender, username=request.user.username).order_by('-id')
    loan = Loan.objects.get(id=1)
    acc_ = Account.objects.get(user_id=request.user.id)
    monthly = MonthlyActivity.objects.get(member=request.user.username)
    turn = Turn.objects.get(member=request.user.username)
    applies = Apply.objects.filter(member=request.user.username).order_by('-id')
    logs = ActivityLog.objects.filter(user=request.user.username).order_by('-id')
    return render(request, 'notification.html',
                  {'loan': loan, 'account': acc_, 'monthly': monthly, 'turn': turn, 'apply': applies, 'logs': logs,
                   'notification': notify})


# admin

def admin(request):
    loan = Loan.objects.get(id=1)
    acc = Account.objects.get(user_id=request.user.id)
    acc_ = Account.objects.all()
    monthly = MonthlyActivity.objects.get(member=request.user.username)
    turn = Turn.objects.get(member=request.user.username)
    applies = Apply.objects.filter(member=request.user.username).order_by('-id')
    logs = ActivityLog.objects.filter(user=request.user.username).order_by('-id')
    logs1 = ActivityLog.objects.filter(user=request.user.username).order_by('-id').first()
    notification = Notification.objects.filter(username=request.user.username).order_by('-id')[:3]
    return render(request, 'admin.html',
                  {'loan': loan, 'account': acc_, 'account1': acc, 'monthly': monthly, 'turn': turn, 'apply': applies,
                   'logs': logs, 'logs1': logs1,
                   'notification': notification})


def edit_user(request, username):
    if request.method == 'POST':
        form = EditUserForm(request.POST)
        if form.is_valid():
            new_turn = form.cleaned_data['turn']
            new_status = form.cleaned_data['status']

            if new_status == 'verify':
                status = 1
            else:
                status = 0

            turn = Turn.objects.get(member=username)
            acc = Account.objects.get(name=username)

            acc.status = status
            acc.save()
            turn.number = new_turn
            turn.save()
            messages.success(request, "User data updated successfully")

            return redirect('admin')

    else:
        turn = Turn.objects.get(member=username)
        acc1 = Account.objects.get(name=username)
        initial_data = {'turn': turn.number, 'status': acc1.status}
        form = EditUserForm(initial=initial_data)

        loan = Loan.objects.get(id=1)
        acc = Account.objects.get(user_id=request.user.id)
        acc_ = Account.objects.all()
        monthly = MonthlyActivity.objects.get(member=request.user.username)
        applies = Apply.objects.filter(member=request.user.username).order_by('-id')
        logs = ActivityLog.objects.filter(user=request.user.username).order_by('-id')
        logs1 = ActivityLog.objects.filter(user=request.user.username).order_by('-id').first()
        notification = Notification.objects.filter(username=request.user.username).order_by('-id')[:3]

    return render(request, 'edituser.html', {'form': form, 'acc': acc1, 'turn': turn,
                                             'loan': loan, 'account': acc_, 'account1': acc, 'monthly': monthly,
                                             'turn': turn, 'apply': applies,
                                             'logs': logs, 'logs1': logs1,
                                             'notification': notification}
                  )


def loan_application(request):
    apply = Apply.objects.all()
    acc_ = Account.objects.get(name=request.user.username)

    return render(request, 'loan_application.html', {'apply': apply, 'account': acc_})


def approve_user(request, username):
    apply = Apply.objects.get(member=username, type=0)
    apply.status = 'approved'
    apply.save()
    loan_amount = apply.amount
    messages.success(request, 'You have successfully approved loan for ' + username)
    formatted_message = "Dear " + username + ",\n\n" \
                                             "The loan you applied for of KES " + str(
        loan_amount) + " is successful. Please " \
                       "check your M-pesa account after a few minutes.\n\n" \
                       "Best regards,\n" \
                       "~ Admin Family Bank"

    message_approved = Notification(type='info', username=username, sender='Admin',
                                    message=formatted_message, subject='Loan Approval')
    message_approved.save()
    send_message(formatted_message)
    return redirect('loan_application')


def reject_user(request, username):
    reject = Apply.objects.get(member=username, type=0)
    loan_amount = reject.amount
    reject.delete()
    loan = Loan.objects.get(id=1)
    loan.loan = loan.loan + loan_amount
    loan.save()
    messages.success(request, 'You have successfully rejected loan for ' + username)
    formatted_message = "Dear " + username + ",\n\n" \
                                             "The loan you applied for of KES " + str(
        loan_amount) + " has been rejected by the Admin. " \
                       "If you think this is a mistake contact Admin\n\n" \
                       "Best regards,\n" \
                       "~ Admin Family Bank"

    message_approved = Notification(type='info', username=username, sender='Admin',
                                    message=formatted_message, subject='Loan Rejection')
    message_approved.save()
    send_message(formatted_message)
    return redirect('loan_application')


def loan_repayment(request):
    global profit
    apply = Apply.objects.all()
    acc_ = Account.objects.get(name=request.user.username)
    for app in apply:
        profit = app.amount * app.interest_rate / 100

    return render(request, 'loan_payment.html', {'apply': apply, 'account': acc_, 'profit': profit})


def loan_repay(request, username):
    if request.method == 'POST':
        paid = int(request.POST['paid'])
        apply = Apply.objects.get(member=username, type=0)
        loan = int(apply.amount) + int(apply.amount * Decimal('0.1'))

        if paid == loan:
            apply.type = 1
            apply.save()
            _paidLoan = PayLoan(member=username, payment_amount=paid)
            _paidLoan.save()
            x = Loan.objects.get(id=1)
            x.loan = x.loan + paid
            x.save()

            messages.success(request, 'Full Payment updated successfully!')
            formatted_message = f"Dear {username},\n\n Payment of KES {paid} " \
                                "received is used to fully pay your loan. \n" \
                                "You do not have an outstanding loan\n\n.Best Regards, \n~Family Bank Team."

            message_approved = Notification(type='team', username=username, sender='Admin',
                                            message=formatted_message, subject='Loan Payment')
            message_approved.save()
            send_message(formatted_message)
            return redirect('loan_repayment')
        elif loan > paid:
            _loan = loan - paid
            __loan = int(_loan + _loan * Decimal('0.1'))
            apply.amount = _loan
            apply.type = 0
            current_date = datetime.now().date()
            date_due = current_date + timedelta(days=30)
            apply.date_due = date_due
            apply.save()
            x = Loan.objects.get(id=1)
            x.loan = x.loan + paid
            x.save()
            messages.success(request, 'Payment updated successfully!')
            formatted_message = f"Dear {username},\n\n Payment of KES {paid} " \
                                f"received is used to pay your loan partially. \n" \
                                f"Your outstanding loan balance is KES {__loan} due {date_due}. " \
                                "\n\nRegards,\n~ Family Bank Team."

            message_approved = Notification(type='team', username=username, sender='Admin',
                                            message=formatted_message, subject='Loan Payment')
            message_approved.save()
            send_message(formatted_message)

            _paidLoan = PayLoan(member=username, payment_amount=paid)
            _paidLoan.save()
            return redirect('loan_repayment')
    else:
        acc = Account.objects.get(name=username)
        apply = Apply.objects.get(member=username, type=0)
        loan = int(apply.amount + apply.amount * Decimal('0.1'))
        return render(request, 'loan_pay.html', {'account': acc, 'loan': loan, 'apply': apply})


def contribution(request):
    form = ContributionForm

    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            selected_username = form.cleaned_data['username']
            current_month = datetime.now().month
            current_year = datetime.now().year
            month_name = calendar.month_name[current_month]  # Get the month name

            contribute = Contribution(member=selected_username, amount=1500, contribution_month=current_month,
                                      contribution_year=current_year)
            contribute.save()

            contributions = Contribution.objects.filter(
                contribution_month=current_month,
                contribution_year=current_year
            )
            # Create a dictionary to store contributions by member
            contributions_by_member = defaultdict(Decimal)

            # Calculate the total contributions and organize them by member
            for contribution in contributions:
                contributions_by_member[contribution.member] += contribution.amount

            # Create the message listing paid members and their contributions
            message = "Hello Family below is a list of Paid Members for the month of {} {}\n".format(month_name,
                                                                                                     current_year)
            total_amount = Decimal(0)

            for member, amount in contributions_by_member.items():
                message += "{} - {} \n".format(member, amount)
                total_amount += amount

            message += "\n\nTotal - {} \n".format(total_amount)
            send_message(message)

            _contrib = MonthlyActivity.objects.get(member=selected_username)
            _contrib.total_contributions = _contrib.total_contributions + 1500
            _contrib.aggregate_balance = _contrib.aggregate_balance + 500
            _contrib.save()

            _loan = Loan.objects.get(id=1)
            _loan.loan = _loan.loan + 500
            _loan.save()

            messages.success(request, 'successfully updated Monthly contribution')
            formatted_message = f"Dear {selected_username},\n\n Payment of KES 1500 " \
                                "received for your monthly contributions." \
                                "\n\nRegards, \n~Family Bank Team."

            message_approved = Notification(type='info', username=selected_username, sender='Admin',
                                            message=formatted_message, subject='Monthly contribution Recieved!')
            message_approved.save()
            send_message(formatted_message)
            return redirect('contribution')

    else:

        current_month = datetime.now().month
        current_year = datetime.now().year
        _contribute = Contribution.objects.filter(contribution_month=current_month, contribution_year=current_year)
        return render(request, 'monthlycontibution.html', {'form': form, 'contribute': _contribute})
