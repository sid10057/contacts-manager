from flask import Flask  ,render_template,request,redirect,url_for, flash, get_flashed_messages# pip install Flask
from flask_mysqldb import MySQL 
import requests, json
import yaml

# Pass in name to determine root path, then Flask can find other files easier
app = Flask(__name__)
app.secret_key='6LfZQIcUAAAAAL50t1xAoPCbQcp0f7kC_vjtrsgD'
# Configure db
db=yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB']  = db['mysql_db']

mysql=MySQL(app)

	
# Route - mapping (connecting) a URL to Python function
@app.route('/',methods=['GET', 'POST'])
def index():
	sitekey = "6LfZQIcUAAAAAFX_u19mgDT6nBebRR5HnFpzEv_0"
	if request.method == 'POST':
		#fetch form data
		userdetails = request.form
		name = userdetails['name']
		email = userdetails['email']
		hall = userdetails['hall']
		branch = userdetails['branch']
		captcha_response = request.form['g-recaptcha-response']
		if is_human(captcha_response):
            # Process request here
			status ="Detail submitted successfully."
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO users(name,email,hall,branch) VALUES(%s,%s,%s,%s)",(name,email,hall,branch))
			mysql.connection.commit()
			cur.close()
		else:
             # Log invalid attempts
			status = "Sorry ! Bots are not allowed."

		flash(status)
		return redirect('/')
	return render_template('index.html')


def is_human(captcha_response):
	""" Validating recaptcha response from google server.
	    Returns True captcha test passed for the submitted form 
	    else returns False.
	"""
	secret = "6LfZQIcUAAAAAL50t1xAoPCbQcp0f7kC_vjtrsgD"
	payload = {'response':captcha_response, 'secret':secret}
	response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
	response_text = json.loads(response.text)
	return response_text['success']


@app.route('/usersearch',methods=['POST'])
def usersearch():
	#fetch form data
	userdetails = request.form
	entry=userdetails['search']
	category=userdetails['category']
	cur=mysql.connection.cursor()
	if  category== 'name' :
		num = cur.execute("SELECT * FROM users WHERE name LIKE %s ",['%'+entry+'%'])
	elif  category== 'email' :
		num = cur.execute("SELECT * FROM users WHERE email LIKE %s ",['%'+entry+'%'])
	elif  category== 'hall' :
		num = cur.execute("SELECT * FROM users WHERE hall LIKE %s ",['%'+entry+'%'])
	else  :
		num = cur.execute("SELECT * FROM users WHERE branch LIKE %s ",['%'+entry+'%'])
	if num>0 :
		userinfo=cur.fetchall()
		return render_template('user.html',userdetails=userinfo)
	else :
		return 'NO MATCH FOUND '

@app.route('/users')
def users():
	cur=mysql.connection.cursor()
	num = cur.execute("SELECT * FROM users")
	if num>0 :
		userdetails=cur.fetchall()
		return render_template('user.html',userdetails=userdetails)


# Runs app only when we run this script directly, not if we import this somewhere else
if __name__ == "__main__":
    app.run(debug=True)