from typing import Counter
import psycopg2
CONNECTION = "postgres://postgres:nitin@localhost:5432/factory"

conn = psycopg2.connect(CONNECTION)

def machine():
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        create_machine =  """CREATE TABLE machine (
                                           id SERIAL PRIMARY KEY,
                                           description text,
                                           loading_time INTEGER,
                                           setup_time INTEGER
                                           );"""
        
        cursor.execute(create_machine)
        conn.commit()
        cursor.close()

#machine()


def product():
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        create_product =  """CREATE TABLE product (
                                           id SERIAL PRIMARY KEY,
                                           description text
                                           );"""
        
        cursor.execute(create_product)
        conn.commit()
        cursor.close()

#product()

def layout():
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS layout')
        create_layout =  """CREATE TABLE layout (
                                           id SERIAL PRIMARY KEY,
                                           machine_id INTEGER,
                                           previous INTEGER,
                                           next INTEGER,
                                           FOREIGN KEY (machine_id) REFERENCES machine (id)
                                           );"""
        
        cursor.execute(create_layout)
        conn.commit()
        cursor.close()


#layout()

def switch():
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        create_switch =  """CREATE TABLE switch (
                                           id SERIAL PRIMARY KEY,
                                           machine_id INTEGER,
                                           description text,
                                           FOREIGN KEY (machine_id) REFERENCES machine (id)
                                           );"""
        
        cursor.execute(create_switch)
        conn.commit()
        cursor.close()

#switch()

def metre():
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        create_metre =  """CREATE TABLE metre (
                                           id SERIAL PRIMARY KEY,
                                           machine_id INTEGER,
                                           description text,
                                           units text,
                                           UB INTEGER,
                                           LB INTEGER,
                                           FOREIGN KEY (machine_id) REFERENCES machine (id)
                                           );"""
        
        cursor.execute(create_metre)
        conn.commit()
        cursor.close()

#metre()

def cycle_time():
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        create_cycletime =  """CREATE TABLE Cycle_Time (
                                           id SERIAL PRIMARY KEY,
                                           machine_id INTEGER,
                                           product_id INTEGER,
                                           cycle_time INTEGER,
                                           cycle_deviation INTEGER,
                                           FOREIGN KEY (machine_id) REFERENCES machine (id),
                                           FOREIGN KEY (product_id) REFERENCES product (id)
                                           );"""
        
        cursor.execute(create_cycletime)
        conn.commit()
        cursor.close() 
        
#cycle_time()

def switch_data():
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        create_switchdata = """CREATE TABLE Switch_Data (
                                           time TIMESTAMPTZ NOT NULL,
                                           status INTEGER,
                                           switch_id INTEGER,
                                           FOREIGN KEY (switch_id) REFERENCES switch (id)
                                           );"""      
        cursor.execute(create_switchdata)
        conn.commit()
        cursor.close()


#switch_data()

def switch_data_hypertable():
    with psycopg2.connect(CONNECTION) as conn:
        query_create_switchdata_hypertable = "SELECT create_hypertable('Switch_Data', 'time');" #"ALTER EXTENSION timescaledb UPDATE;"
        cursor = conn.cursor()
        cursor.execute(query_create_switchdata_hypertable)
        conn.commit()
        cursor.close()

def metre_data():
    with psycopg2.connect(CONNECTION) as conn:
        query_create = """CREATE TABLE metre_data (
                            time TIMESTAMPTZ NOT NULL,
                            metre_id INTEGER,
                            reading DOUBLE PRECISION,
                            FOREIGN KEY (metre_id) REFERENCES metre (id)
                            );"""
        cursor = conn.cursor()
        cursor.execute(query_create)
        conn.commit()
        cursor.close()

#metre_data()

def metre_data_hypertable():
    with psycopg2.connect(CONNECTION) as conn:
        query_create = """SELECT create_hypertable('metre_data', 'time');"""
        cursor = conn.cursor()
        cursor.execute(query_create)
        conn.commit()
        cursor.close()

#metre_data_hypertable()

def job_data():
    with psycopg2.connect(CONNECTION) as conn:
        query_create = """CREATE TABLE job_data (
                            time TIMESTAMPTZ NOT NULL,
                            product_id INTEGER, 
                            status text,
                            machine_id INTEGER,
                            job_no INTEGER,
                            FOREIGN KEY (machine_id) REFERENCES machine (id),
                            FOREIGN KEY (product_id) REFERENCES product (id)
                            );"""
        cursor = conn.cursor()
        cursor.execute(query_create)
        conn.commit()
        cursor.close()

#job_data()
def job_data_hypertable():
    with psycopg2.connect(CONNECTION) as conn:
        query_create = """SELECT create_hypertable('job_data', 'time');"""
        cursor = conn.cursor()
        cursor.execute(query_create)
        conn.commit()
        cursor.close()

# machine()
# product()
# layout()
# switch()
# metre()
# cycle_time()
# switch_data()
# metre_data()
# job_data()
# switch_data_hypertable()
# job_data_hypertable()
# metre_data_hypertable()