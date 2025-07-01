import re
from flask import Flask, render_template, redirect, session, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask_migrate import Migrate
from datetime import datetime, timedelta, timezone
import random
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import uuid
import requests
from fg import Result 

# -------------------- App Configuration --------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1886012d'

# Mail Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True  # ❌ This should be True
app.config['MAIL_USERNAME'] = 'sahwahflaviusmiechak28@gmail.com'  # ❌ This should be your full Gmail address
app.config['MAIL_PASSWORD'] = 'Sahwahflavius12$'  # ❗Should be an App Password
app.config['MAIL_DEFAULT_SENDER'] = 'sahwahflaviusmiechak28@gmail.com'
# -------------------- Extensions Init --------------------
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -------------------- Sentry Initialization --------------------
sentry_sdk.init(
    dsn="https://d4cd773b0dc3760556bef7282f9cddea@o4508779983994880.ingest.us.sentry.io/4508780021415936",  # Replace with your Sentry DSN
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,  # Adjust for performance monitoring
    send_default_pii=True    # To capture user info if available
)

# -------------------- Models --------------------


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    
    username = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    ssn = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    otp_code = db.Column(db.String(6))
    otp_expiration = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(100), nullable=False, default='user')
    bank = db.relationship('Bank', back_populates='user', uselist=False, foreign_keys='Bank.user_id')
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    wallet = db.relationship("Wallet", backref="user", uselist=False)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))  # 'deposit' or 'withdrawal'
    amount = db.Column(db.Float)
    method = db.Column(db.String(10))  # 'mtn' or 'orange'
    status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reference = db.Column(db.String(100))

class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_balance = db.Column(db.Float)
    account_number = db.Column(db.String(50), nullable=False)
    routing_number = db.Column(db.String(50), nullable=False)
    account_balance = db.Column(db.Float, nullable=False, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='bank', foreign_keys=[user_id])
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(20), nullable=False)
    card_expiry = db.Column(db.String(10), nullable=False)
    card_cvv = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('card', uselist=False))

class Transfer(db.Model):
    __tablename__ = 'transfers'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    net_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_transfers')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_transfers')

    def __repr__(self):
        return f"<Transfer {self.id}: {self.sender_id} → {self.receiver_id} | Amount: {self.amount}>"
# -------------------- Login Management --------------------
# -------------------- Login Management --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

@app.before_request
def set_sentry_user():
    if current_user.is_authenticated:
        sentry_sdk.set_user({
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username
        })
    else:
        sentry_sdk.set_user(None)

# -------------------- Helper Functions --------------------
def generate_account_number():
    return str(random.randint(10**9, 10**10 - 1))

def generate_routing_number():
    return str(random.randint(10**8, 10**9 - 1))

def generate_card_number():
    return '4' + ''.join([str(random.randint(0, 9)) for _ in range(15)])

def generate_card_expiry():
    expiry_date = datetime.now() + timedelta(days=3*365)
    return expiry_date.strftime("%m/%y")

def generate_card_cvv():
    return ''.join([str(random.randint(0, 9)) for _ in range(3)])

# -------------------- Auth Routes --------------------

@app.route('/fix-missing-banks')
@login_required
def fix_missing_banks():
    if current_user.role not in ['admin', 'super_admin']:
        flash("Access denied")
        return redirect(url_for('home'))
    fixed = 0
    for user in User.query.all():
        if not user.bank:
            bank = Bank(
                account_number=generate_account_number(),
                routing_number=generate_routing_number(),
                account_balance=5000.0,
                user_id=user.id
            )
            db.session.add(bank)
            fixed += 1
    db.session.commit()
    flash(f"Fixed {fixed} users without bank accounts.")
    return redirect(url_for('admin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        if User.query.filter_by(email=data['email']).first():
            flash('Email already exists')
        else:
            new_user = User(
                username=data['username'], firstname=data['firstname'], lastname=data['lastname'],
                phone=data['phone'], email=data['email'], ssn=data['ssn'],
                address=data['address'], zipcode=data['zipcode']
            )
            new_user.set_password(data['password'])
            db.session.add(new_user)
            db.session.flush()

            db.session.add(Bank(
                account_number=generate_account_number(),
                routing_number=generate_routing_number(),
                user_id=new_user.id
            ))
            db.session.add(Card(
                card_number=generate_card_number(),
                card_expiry=generate_card_expiry(),
                card_cvv=generate_card_cvv(),
                user_id=new_user.id
            ))
            db.session.commit()
            flash("Account created successfully!")
            return redirect(url_for('login'))
    return render_template('auth/signup.html')

def send_otp_email(user):
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expiration = datetime.utcnow() + timedelta(minutes=5)
    db.session.commit()

    msg = Message(
        subject="Your OTP Code",
        recipients=[user.email],
        body=f"Hello {user.firstname},\n\nYour OTP code is {otp}. It expires in 5 minutes."
    )
    mail.send(msg)


@app.route('/verify-otp', methods=['GET', 'POST'])
@login_required
def verify_otp():
    if request.method == 'POST':
        code = request.form.get('otp')
        if (
            current_user.otp_code == code and
            current_user.otp_expiration > datetime.utcnow()
        ):
            current_user.is_verified = True
            current_user.otp_code = None  # clear used OTP
            db.session.commit()
            flash("OTP verified successfully!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid or expired OTP", "danger")
    return render_template('verify_otp.html')

@app.route('/resend-otp')
@login_required
def resend_otp():
    if current_user.is_verified:
        flash("Your account is already verified.", "info")
        return redirect(url_for('home'))

    send_otp_email(current_user)
    flash("A new OTP has been sent to your email.", "success")
    return redirect(url_for('verify_otp'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if not user.is_verified:
                send_otp_email(user)
                return redirect(url_for('verify_otp'))
            return redirect(url_for('admin' if user.role in [ 'user', 'admin', 'super_admin'] else 'home'))
        flash('Invalid email or password')
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# -------------------- Main Routes --------------------
@app.route('/')
@login_required
def home():
    if current_user.is_authenticated:
        user = current_user
        transactions = sorted(
            user.sent_transfers + user.received_transfers,
            key=lambda t: t.timestamp,
            reverse=True
        )
        # Combine sent and received, then sort by timestamp descending
        return render_template(
            'vd.html',
            user=current_user,
            transactions=transactions,
            current_date=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    else:
        return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    if current_user.role not in ['admin', 'super_admin','moderator', 'manager']:
        flash('Access denied')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin.html', users=users, highlight_user_id=request.args.get('highlight_user_id', type=int))

@app.route('/edit_user/<int:user_id>')
@login_required
def edit_user(user_id):
    return render_template('edit_user.html', user=User.query.get(user_id))
@app.route('/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    user = User.query.get(user_id)
    user.firstname = request.form.get('firstname')
    user.lastname = request.form.get('lastname')
    user.email = request.form.get('email')
    user.role = request.form.get('role')
    
    # If you're trying to update the user's bank balance as well:
    if user.bank:
        try:
            user.bank.account_balance = float(request.form.get('account_balance', user.bank.account_balance))
        except ValueError:
            flash("Invalid balance value.", "danger")

    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    db.session.delete(User.query.get(user_id))
    db.session.commit()
    return redirect(url_for('admin'))

# -------------------- Bank/Card Routes --------------------
@app.route('/add_bank_card', methods=['GET', 'POST'])
@login_required
def add_bank_card():
    if request.method == 'POST':
        data = request.form
        db.session.add(Bank(account_number=data['account_number'], routing_number=data['routing_number'], user_id=current_user.id))
        db.session.add(Card(card_number=data['card_number'], card_expiry=data['card_expiry'], card_cvv=data['card_cvv'], user_id=current_user.id))
        db.session.commit()
        flash("Bank and Card details saved.")
        return redirect(url_for('home'))
    return render_template('add_bank_card.html')

@app.route('/view_cards')
@login_required
def view_cards():
  
  return render_template('Card.html', users=User.query.all(), cards = Card.query.all())



@app.route('/view_bank_accounts')
def view_bank_accounts():
    return render_template('bank.html')

@app.route('/search_by_account')
@login_required
def search_by_account():
    if current_user.role not in ['admin', 'super_admin']:
        flash("Access denied")
        return redirect(url_for('home'))
    account = Bank.query.filter_by(account_number=request.args.get('account_number')).first()
    if account:
        return redirect(url_for('admin', highlight_user_id=account.user_id))
    flash("No user found with that account number")
    return redirect(url_for('admin'))

@app.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.get_json()
    account = Bank.query.filter_by(account_number=data.get('account_number')).first()
    if not account:
        return jsonify({'message': 'Account not found'}), 404
    try:
        account.account_balance = float(data.get('account_balance'))
        db.session.commit()
        return jsonify({'message': 'Balance successfully updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating balance', 'error': str(e)}), 500

# -------------------- Deposit Route --------------------
@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            method = request.form.get('method')
            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                return redirect(url_for('deposit'))

            super_admin = User.query.filter_by(role='super_admin').first()
            if not super_admin or not super_admin.bank:
                flash("Super Admin account not found.", "danger")
                return redirect(url_for('deposit'))

            if method == 'bank' and (not current_user.bank or current_user.bank.account_balance < amount):
                flash("Insufficient funds.", "danger")
                return redirect(url_for('deposit'))

            if method == 'bank':
                current_user.bank.account_balance -= amount
            super_admin.bank.account_balance += amount
            db.session.commit()

            msg = Message(
                "New Deposit Received",
                recipients=[super_admin.email],
                body=f"A deposit of ${amount:.2f} has been made to your account via {method.upper()}.\nFrom: {current_user.firstname} {current_user.lastname} ({current_user.email})"
            )
            mail.send(msg)

            flash(f"${amount:.2f} deposited and email sent to Super Admin.", "success")
            return render_template('deposit_success.html', amount=amount, method=method)
        except Exception as e:
            db.session.rollback()
            flash("Deposit failed: " + str(e), "danger")
            return render_template('deposit_fail.html', error=str(e))
    return render_template('Deposit.html', account_number=current_user.bank.account_number if current_user.bank else "N/A")
#--------filter------
@app.template_filter('spaced_card')
def spaced_card(card_number):
    # Ensure it's a string and strip any existing spaces
    card_number = str(card_number).replace(" ", "")
    return ' '.join(card_number[i:i+4] for i in range(0, len(card_number), 4))

# -------------------- Misc --------------------


#-------------payments routing-----------
# Utility: apply a 5% fee and send to super admin
def apply_fee(amount):
    fee = amount * 0.05
    net_amount = amount - fee
    return net_amount, fee

def send_fee_to_admin(fee):
    admin = User.query.filter_by(role='super_admin').first()
    if admin and admin.bank:
        admin.bank.account_balance += fee
        db.session.commit()

@app.route('/get-user-by-identifier', methods=['POST'])
def get_user_by_identifier():
    data = request.json
    identifier = data.get('identifier')

    if not identifier:
        return jsonify({'error': 'Identifier is required'}), 400

    user = (
        db.session.query(User)
        .join(Bank, User.id == Bank.user_id)
        .join(Card, User.id == Card.user_id)
        .filter(
            (User.phone== identifier) |
            (Bank.account_number == identifier) |
            (Card.card_number == identifier)
        )
        .first()
    )

    if user:
          # Access related Bank record
        bank = Bank.query.filter_by(user_id=user.id).first()
        full_name = f"{user.firstname} {user.lastname}"
        account_number = bank.account_number if bank else 'N/A'

        return jsonify({
            'name': full_name,
            'email': user.email,
            'account': account_number
        })
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/transfer', methods=['POST'])
def transfer():
    try:
        print("Received transfer request")
        data = request.json
        print(f"Request data: {data}")

        if not data or 'receiver' not in data or 'amount' not in data:
            return jsonify({'error': 'Missing receiver or amount'}), 400

        # Authenticate sender (using Flask-Login or hardcoded user)
        sender = current_user  # Or: User.query.get(1)
        amount = float(data['amount'])
        receiver_identifier = data['receiver']

        # Determine receiver by account number, phone, or card
        receiver = (
            db.session.query(User)
            .join(Bank, User.id == Bank.user_id)
            .join(Card, User.id == Card.user_id)
            .filter(
                (Bank.account_number == receiver_identifier) |
                (User.phone == receiver_identifier) |
                (Card.card_number == receiver_identifier)
            )
            .first()
        )

        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 400

        if sender.id == receiver.id:
            return jsonify({'error': 'Cannot transfer to yourself'}), 400

        if sender.bank.account_balance < amount:
            return jsonify({'error': 'Insufficient funds'}), 400

        net_amount, fee = apply_fee(amount)
        print(f"Net amount: {net_amount}, Fee: {fee}")

        # Update balances
        sender.bank.account_balance -= amount
        receiver.bank.account_balance += net_amount
        send_fee_to_admin(fee)

        # Record the transfer
        transfer_record = Transfer(
            sender_id=sender.id,
            receiver_id=receiver.id,
            amount=amount,
            fee=fee,
            net_amount=net_amount
        )
        db.session.add(transfer_record)
        db.session.commit()

        return jsonify({
            'message': 'Transfer successful',
            'fee': fee,
            'net_amount': net_amount,
            'transfer_id': transfer_record.id
        }), 200

    except Exception as e:
        print("Exception occurred:", str(e))
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# -------------------- Payment Routes --------------------
@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'GET':
        # Render withdrawal form for browser users

        return render_template('withdraw.html', user=current_user)

    # Handle POST (API or form)
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # Always use the logged-in user for security
    user = current_user

    try:
        amount = float(data.get('amount', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid amount'}), 400

    method = data.get('method', '').lower()
    phone = data.get('phone', '').strip()

    if method not in ['bank', 'mtn', 'orange']:
        return jsonify({'error': 'Invalid or missing withdrawal method'}), 400

    # For mobile money, phone number is required and must match pattern
    if method in ['mtn', 'orange']:
        if not phone:
            return jsonify({'error': 'Phone number is required for mobile money withdrawal'}), 400
        # Example: MTN Cameroon pattern
        import re
        if not re.match(r'^\+2376\d{8}$', phone):
            return jsonify({'error': 'Invalid phone number format. Use +2376XXXXXXXX'}), 400

    # Check user and balance
    if not user or not user.bank or user.bank.account_balance < amount or amount <= 0:
        return jsonify({'error': 'Invalid user or insufficient funds'}), 400

    net_amount, fee = apply_fee(amount)
    user.bank.account_balance -= amount
    send_fee_to_admin(fee)

    if method == 'bank':
        # Bank withdrawal logic
        if user.bank.account_balance < net_amount:
            db.session.rollback()
            return jsonify({'error': 'Insufficient funds for bank withdrawal'}), 400
        user.bank.account_balance -= net_amount
        transaction = Transaction(
            type='withdrawal',
            amount=amount,
            method='bank',
            status='completed',
            user_id=user.id,
            reference=str(uuid.uuid4())
        )
        db.session.add(transaction)
        # Update the bank account balance
        user.bank.account_balance -= net_amount
        # Commit the changes

        db.session.commit()
        return jsonify({'message': f'Bank withdrawal of {net_amount} successful', 'fee': fee}), 200

    elif method == 'mtn':
        # MTN Mobile Money withdrawal logic
        from accesst import DISBURSMENT_SUBSCRIPTION_KEY, DISBURSMENT_USER_ID, DISBURSMENT_API_KEY
        import uuid, requests
        from requests.auth import HTTPBasicAuth

        reference_id = str(uuid.uuid4())
        token_url = "https://sandbox.momodeveloper.mtn.com/disbursement/token/"
        token_headers = {
            "Ocp-Apim-Subscription-Key": DISBURSMENT_SUBSCRIPTION_KEY
        }
        token_response = requests.post(
            token_url,
            headers=token_headers,
            auth=HTTPBasicAuth(DISBURSMENT_USER_ID, DISBURSMENT_API_KEY),
            timeout=30
        )
        if token_response.status_code != 200:
            db.session.rollback()
            return jsonify({'error': 'Failed to get MTN access token', 'details': token_response.text}), 500
        access_token = token_response.json().get("access_token")

        transfer_url = "https://sandbox.momodeveloper.mtn.com/disbursement/v1_0/transfers"

        transfer_headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": "sandbox",
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": DISBURSMENT_SUBSCRIPTION_KEY
        }
        transfer_payload = {
            "amount": f"{net_amount:.2f}",
            "currency": "XAF",
            "externalId": str(user.id),
            "payee": {
                "partyIdType": "MSISDN",
                "partyId": phone
            },
            "payerMessage": "Withdrawal from bank account to momo",
            "payeeNote": "Withdrawal"
        }
        transfer_response = requests.post(
            transfer_url,
            headers=transfer_headers,
            json=transfer_payload,
            timeout=30
        )
        if transfer_response.status_code == 202:
            db.session.commit()
            return jsonify({'message': f'MTN withdrawal of {net_amount} sent to {phone}', 'fee': fee, 'reference_id': reference_id}), 200
        else:
            db.session.rollback()
            return jsonify({'error': 'MTN withdrawal failed', 'details': transfer_response.text}), 200

    elif method == 'orange':
        # Set credentials and URL
        from config import ORANGE_CLIENT_ID, ORANGE_CLIENT_SECRET
        from requests.auth import HTTPBasicAuth
        auth_url = "https://api.orange.com/oauth/v3/token"

        # Get access token
        token_response = requests.post(
            auth_url,
            data={"grant_type": "client_credentials"},
            auth=HTTPBasicAuth(ORANGE_CLIENT_ID, ORANGE_CLIENT_SECRET)
        )

        if token_response.status_code != 200:
            return jsonify({'error': 'Failed to authenticate with Orange API', 'details': token_response.text}), 500

        access_token = token_response.json().get("access_token")

        # Prepare transfer request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "amount": f"{net_amount:.2f}",
            "currency": "XAF",
            "receiver": phone,  # Ensure format: +2376XXXXXXX
            "description": "Withdrawal to Orange Money"
        }

        response = requests.post(
            "https://api.orange.com/orange-money-transfers/v1/transfer",  # Replace with real endpoint
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            db.session.commit()
            return jsonify({'message': f'Orange withdrawal of {net_amount} sent to {phone}', 'fee': fee}), 200
        else:
            db.session.rollback()
            return jsonify({'error': 'Orange withdrawal failed', 'details': response.text}), 500




@app.route('/merchant-payment', methods=['POST'])
def merchant_payment():
    return transfer()  # similar to a user transfer to a merchant

@app.route('/service-payment', methods=['POST'])
def service_payment():
    return transfer()  # same logic; adjust receiver as service provider




# Add this route to your Flask app
@app.route('/api/get-balance')
@login_required
def get_balance():
    return jsonify({'balance': current_user.bank.account_balance})


# -------------------- Main --------------------

if __name__ == '__main__':
    app.run(debug=True)
