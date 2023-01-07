from flask import Flask,session,render_template,redirect,url_for,request,Blueprint,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import datetime
import psycopg2
from flask_session import Session
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:nitin@localhost:5432/timeseries"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.secret_key = 'ADHGHASUDAWHAWF'
app.config['SESSION_TYPE'] = 'filesystem'
CONNECTION = "postgres://postgres:nitin@localhost:5432/timeseries"
@app.route('/',methods=['GET','POST'])
def home():
    return render_template('home.html')
@app.route('/machine/<id>',methods=['GET','POST'])
def machine(id):
    id=str(id)
    session["temp_id"] =id
    with psycopg2.connect(CONNECTION) as conn:
        query = """select * from layout
                    where machine_id=(%s); """
        cursor = conn.cursor()
        cursor.execute(query,id)
        layout=(cursor.fetchall())
        query = """select * from metre
                    where machine_id=(%s); """
        cursor = conn.cursor()
        cursor.execute(query,id)
        metres=(cursor.fetchall())
        query = """select * from switch
                    where machine_id=(%s); """
        cursor = conn.cursor()
        cursor.execute(query,id)
        switches=(cursor.fetchall())
    return render_template('switch.html',switches=switches,metres=metres,layout=layout)
@app.route('/line/<id>')
def line(id):
    with psycopg2.connect(CONNECTION) as conn:
        query = """select * from switch_data
                    where switch_id=(%s); """
        cursor = conn.cursor()
        cursor.execute(query,(id,))
        switch_data_list=cursor.fetchall()
    timestamps=[]
    status=[]
    for i in switch_data_list:
        timestamps.append((i[0].strftime('%H:%M:%S')))
        status.append(i[1])
    return render_template('line.html',timestamps=timestamps,status=status,switch_id=id)
@app.route('/jobs/<id>',methods=['GET','POST'])
def jobs(id):
    id=(id,)
    with psycopg2.connect(CONNECTION) as conn:
        query = """select * from job_data; """
        cursor = conn.cursor()
        cursor.execute(query)
        jobs=(cursor.fetchall())
        query = """select * from job_data
                where job_no=(%s); """
        cursor = conn.cursor()
        cursor.execute(query,id)
        jobs_desc=(cursor.fetchall())
        print(jobs_desc)
        print(jobs_desc[1::2])
    job_no= set()
    for i in jobs:
        job_no.add(i[4])

    job_in=jobs_desc[::2]
    job_out=jobs_desc[1::2]
    job_deets=[]

    for i in range(len(job_in)):
        if i < len(job_out):
            job_deets.append(tuple((job_in[i][1],job_in[i][0],job_out[i][0],(job_out[i][0]-job_in[i][0]).total_seconds(),job_in[i][3])))
        else:
            job_deets.append(tuple((job_in[i][1],job_in[i][0],"N/A","0",job_in[i][3]))) 

    return render_template('job_no.html',job_no=job_no,job_deets=job_deets)


@app.route('/meter/<id>',methods=['GET','POST'])
def meter(id):
    with psycopg2.connect(CONNECTION) as conn:
        query = """SELECT *
                    FROM metre_data
                    WHERE metre_id= (%s)
                    """
        cursor = conn.cursor()
        cursor.execute(query,(id,))
        meter_data=(cursor.fetchall())
        meter_data=meter_data[::5]
        query = """select * from metre
                    where id=(%s); """
        cursor = conn.cursor()
        cursor.execute(query,(id,))
        meter_desc=(cursor.fetchall())
    timestamps=[]
    readings=[]
    for i in meter_data:
        timestamps.append((i[0].strftime('%H:%M:%S')))
        readings.append(i[2])

    return render_template('meter.html',meter_data=meter_data,timestamps=timestamps,readings=readings,upperlimit=meter_desc[0][4],lowerlimit=meter_desc[0][5])
app.run(debug=True)