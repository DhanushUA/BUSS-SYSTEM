import mysql.connector

from flask import *

from dbconnection import *

app=Flask(__name__)

app.secret_key="1234"



import functools


def login_required(func):
    @functools.wraps(func)
    def secure_function():
        if "lid" not in session:
            return render_template('login.html')
        return func()
    return secure_function


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



#--------------login window---------------------------------------

@app.route('/')
def main():
    return render_template('login.html')

@app.route('/u_reg')
def reg_u():
    return render_template('user_reg.html')

@app.route('/login',methods=['post'])
def LOGIN():
    uname=request.form['username']
    password=request.form['password']
    qry="SELECT * FROM login_table WHERE username=%s AND password=%s "
    val=(uname,password)
    res=selectone(qry,val)
    if res is None:
        return '''<script>alert("invalid");window.location="/"</script>'''
    elif res['type']=='admin':
        session['lid'] = res['login_id']
        return '''<script>alert("welcome");window.location="/admin_home"</script>'''
    elif res['type'] == 'user':
        session['lid'] = res['login_id']
        return '''<script>alert("welcome");window.location="/user_home"</script>'''
    else:
        return '''<script>alert("invalid");window.location="/"</script>'''

@app.route('/user_reg',methods=['post'])
def user_reg():
    name=request.form['textfield1']
    username=request.form['textfield2']
    email=request.form['textfield3']
    password=request.form['textfield4']
    qr="select * from login_table where username=%s"
    res=selectone(qr,username)
    print(res)
    if res is  None:
        qry = "insert into login_table values(null,%s,%s,'user')"
        val = (username, password)
        lid = iud(qry, val)
        qry2 = "insert into users values(null,%s,%s,%s,%s,%s)"
        val2 = (name,username,password,email,str(lid))
        iud(qry2, val2)
        return '''<script>alert("success");window.location="/"</script>'''
    else:
        return '''<script>alert("Username exist");window.location="/"</script>'''

#--------------------end login---------------------------------

#-------------------admin window----------------------------------

@app.route('/admin_home')
def admin():
    return render_template('adminindex.html')


@app.route('/manage_trains')
@login_required
def manage_trains():
    # Fetch all train records
    qry=("SELECT * FROM trains")
    res=selectall(qry)
    return render_template('managetrains.html', val=res)

# Route to add a new train
@app.route('/add_train', methods=['POST'])
@login_required
def add_train():
    train_name = request.form['train_name']
    source_station = request.form['source_station']
    destination_station = request.form['destination_station']
    departure_time = request.form['departure_time']
    arrival_time = request.form['arrival_time']
    total_seats = request.form['total_seats']
    date = request.form['date']

    # Insert into database
    qry = "INSERT INTO trains VALUES (null,%s, %s, %s, %s, %s, %s,%s)"
    val = (train_name,source_station, destination_station, departure_time, arrival_time, total_seats,date)
    iud(qry, val)
    return '''<script>alert("success");window.location="/manage_trains"</script>'''
    

# Route to delete a train
@app.route('/delete_train/<int:train_id>')
@login_required
def delete_train(train_id):
    # Delete train from the database
    qry = "DELETE FROM trains WHERE train_id = %s"
    iud(qry, (train_id))
    return '''<script>alert("Deleted");window.location="/manage_trains"</script>'''

# Route to edit a train
# app.py (Flask application)

@app.route('/update_train/<int:train_id>')
@login_required
def edit_train(train_id):
    # Query to fetch the train details using the train ID
    qry = "SELECT * FROM trains WHERE train_id = %s"
    res = selectone(qry, (train_id))  # Assuming 'selectone' is a function that retrieves a single record

    if res is not None:
        # Render the edit_train.html template and pass the train details to it
        return render_template('update_train.html', val=res)
    else:
        return '''<script>alert("Train not found");window.location="/manage_trains"</script>'''



@app.route('/update_train', methods=['post'])
@login_required
def update_train():
    train_id = request.form['train_id'] 
    train_name = request.form['train_name']
    source_station = request.form['source_station']
    destination_station = request.form['destination_station']
    arrival_time = request.form['arrival_time']
    departure_time = request.form['departure_time']
    total_seats = request.form['total_seats']
    date = request.form['date']

    # Update query
    qry = "UPDATE trains SET train_name=%s,source=%s, destination=%s,departure_time=%s, arrival_time=%s,seats=%s,date=%s WHERE train_id=%s"
    val = (train_name,source_station,destination_station,departure_time, arrival_time, total_seats,date,train_id)
    iud(qry, val) 
    return '''<script>alert("Train details updated successfully");window.location="/manage_trains"</script>'''


@app.route('/manage_users')
@login_required
def manage_users():
    # Join the users and login_table, filter out users with type 'admin'
    qry = """
        SELECT users.*, login_table.type 
        FROM users 
        INNER JOIN login_table ON users.login_id = login_table.login_id 
        WHERE login_table.type != 'admin'
    """
    res = selectall(qry)  
    return render_template('manage_users.html', val=res)

@app.route('/delete_user')
@login_required
def delete_user():
    user_id = request.args.get('idusers')
    
    # Get the login_id for the user being deleted
    qry_get_login_id = "SELECT login_id FROM users WHERE idusers = %s"
    login_id = selectone(qry_get_login_id, (user_id))['login_id']
    
    # Delete the user from the users table
    qry_delete_user = "DELETE FROM users WHERE idusers = %s"
    iud(qry_delete_user, (user_id,))
    
    # Delete the corresponding entry from the login_table
    qry_delete_login = "DELETE FROM login_table WHERE login_id = %s"
    iud(qry_delete_login, (login_id,))
    
    return '''<script>alert("User deleted successfully");window.location="/manage_users"</script>'''

@app.route('/manage_bookings')
@login_required
def manage_bookings():
    qry = """
        SELECT b.booking_id, b.passenger_name, b.source_station, b.destination_station, 
        b.seats_booked, t.train_name FROM bookings_table b
        JOIN trains t ON b.train_id = t.train_id
    """
    res = selectall(qry)  # Function to fetch data from the database
    return render_template('manage_bookings.html', val=res)

@app.route('/delete_booking')
@login_required
def delete_booking():
    booking_id = request.args.get('booking_id')
    qry = "DELETE FROM bookings_table WHERE booking_id=%s"
    iud(qry,(booking_id))
    return '''<script>alert("Booking deleted successfully!");window.location="/manage_bookings"</script>'''

@app.route('/view_complaints')
def view_complaints():
    qry = "select title,description from complaints"
    res = selectall(qry)
    return render_template('view_complaints.html',val = res)        

#------------------------end admin----------------------------------------


#------------------------user window----------------------------------------


@app.route('/user_home')
def user():
    return render_template('userindex.html')

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('lid')  # Assuming you store the user ID in the session
    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if user not logged in

    # Fetch user details from the database
    qry = "SELECT * FROM users WHERE idusers = %s"  # Adjust according to your user ID column
    res = selectone(qry, (user_id,))  # Get user details from the database

    if res is None:
        return '''<script>alert("User not found!");window.location="/"</script>'''
    
    return render_template('profile.html', val=res)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user_id = session.get('lid')  # Retrieve user ID from session
    if user_id is None:
        return '''<script>alert("invalid");window.location="/"</script>'''

    name = request.form['name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']  

    # Update the user information in the database
    qry = "UPDATE users SET name=%s, username=%s, email=%s, password=%s WHERE idusers=%s"
    val = (name, username, email, password, user_id)
    iud(qry, val)  # Assuming iud is your insert/update/delete function

    return '''<script>alert("Profile updated successfully!");window.location="/profile"</script>'''

@app.route('/view_train')
@login_required
def view_train():
    # Fetch all trains from the database
    qry = "SELECT * FROM trains WHERE seats > 0"  # Adjust this query based on your database schema
    res = selectall(qry)  # Assuming this function retrieves all train records from the database
    return render_template('view_train.html', val=res)

@app.route('/book_window')
def book_window():
    return render_template('book_train.html')



@app.route('/book_train', methods=['POST'])
@login_required
def book_train():
    # try:
        login_id = session.get('lid')
        passenger_name = request.form['passenger_name']
        source_station = request.form['source_station']
        destination_station = request.form['destination_station']
        seats_booked = int(request.form['seats_booked'])  # Make sure seats_booked is an integer
        train_id = request.args.get('train_id')

        # Validate that the number of seats booked is greater than 0
        if seats_booked <= 0:
            raise ValueError("The number of seats booked must be greater than zero.")
        print("Train ID:", train_id)  # This will help in debugging
        # Check if train_id and user_id are valid (if there are foreign key constraints)
        if not login_id:
            raise ValueError("Invalid login ID ")
        elif not train_id:
            raise ValueError("Invalid train ID.")
        # Update seat count in the trains table
        qry = "UPDATE trains SET seats = seats - %s WHERE train_id = %s AND seats >= %s"
        res = iud(qry, (seats_booked, train_id, seats_booked))
        
        # Check if the update was successful (train might not have enough seats)
        # if res == 0:
        #     return '''<script>alert("Not enough seats available.");window.location="/view_train"</script>'''

        # Insert booking details into bookings_table
        qry2 = "INSERT INTO bookings_table (login_id, train_id, passenger_name, source_station, destination_station, seats_booked) VALUES (%s, %s, %s, %s, %s, %s)"
        iud(qry2, (login_id, train_id, passenger_name, source_station, destination_station, seats_booked))
        return '''<script>alert("Train booked successfully!");window.location="/view_train"</script>'''

    # except Exception as e:
        # Show a detailed error message for debugging
        # return f'''<script>alert("Failed to book the train: {str(e)}");window.location="/view_train"</script>'''

@app.route('/booking_history')
def booking_history():
    user_id = session.get('lid')  # Assuming user is logged in and 'lid' is stored in the session
    qry = """
        SELECT b.booking_id, b.passenger_name, b.source_station, b.destination_station, b.seats_booked, t.train_name FROM bookings_table b JOIN trains t ON b.train_id = t.train_id WHERE b.login_id = %s
    """
    res = selectall2(qry, (user_id))  # Assuming this function fetches data from the database
    return render_template('booking_history.html', val=res)


@app.route('/cancel_booking')
def cancel_booking():
    booking_id = request.args.get('booking_id')
    
    # Retrieve the booking details first to update the train's seat count
    qry1 = "SELECT train_id, seats_booked FROM bookings_table WHERE booking_id = %s"
    booking_details = selectone(qry1, (booking_id,))
    
    if booking_details:
        train_id = booking_details['train_id']
        seats_to_return = booking_details['seats_booked']
        
        # Update the seats count in the trains table
        qry2 = "UPDATE trains SET seats = seats + %s WHERE train_id = %s"
        iud(qry2, (seats_to_return, train_id))
        
        # Delete the booking from the bookings table
        qry3 = "DELETE FROM bookings_table WHERE booking_id = %s"
        iud(qry3, (booking_id,))
        
        return '''<script>alert("Booking cancelled successfully.");window.location="/booking_history"</script>'''
    else:
        return '''<script>alert("Booking not found.");window.location="/booking_history"</script>'''    

@app.route('/complaints')
def complaints():
    return render_template('complaint.html')

@app.route('/register_complaint', methods=['POST'])
def register_complaint():
    title = request.form['title']
    description = request.form['description']
    user_name = session.get('username', 'Anonymous')  # Mock user session
    qry = "INSERT INTO complaints(description,username,title) VALUES (%s,%s,%s)"
    iud(qry,(description,user_name,title))
    return '''<script>alert("Complaint Registered");window.location="/user_home"</script>'''    


#------------------------end user----------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
   