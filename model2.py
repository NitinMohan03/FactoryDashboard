import simpy
import datetime
import random
import psycopg2
import numpy as np
CONNECTION = "postgres://postgres:nitin@localhost:5432/factory"
###########################################variables used   
def gettime(id):
    with psycopg2.connect(CONNECTION) as conn:
        query = """SELECT machine_id,cycle_time,cycle_deviation from cycle_time
                    WHERE product_id=%s """
        cursor = conn.cursor()
        a=(id,)
        cursor.execute(query,a)
        d=dict()
        for i in cursor.fetchall():
            d[i[0]]=[i[1],i[2]]
        conn.commit()
        cursor.close()
        return d
def getproductids():
    with psycopg2.connect(CONNECTION) as conn:
        query = """SELECT id
                    FROM product; """
        cursor = conn.cursor()
        cursor.execute(query)
        a = [item[0] for item in cursor.fetchall()]
        return a
product_cycle=[]
for i in getproductids():
    product_cycle.append(gettime(i))
breakdown = {1: [(1623378600+600,120),(1623378600+840,60)],2 : [(1623378600+1200,120)], 3: [(1623378600+1800,120),(1623378600+2000,60)] , 4 : [(1623378600+2400,120)]}
breakdown2 = {1: [],2 : [], 3: [] , 4 : []}
model_capacity =500
dispatch_capacity = 1000
pre_shaped_capacity=1
pre_planed_capacity=1
pre_honed_capacity=1
seconds = 1623382200
endtime = seconds
initial_model_list=[]
initial_model_list.append((1,33))
initial_model_list.append((2,35))
initial_model_list.append((3,36))
starttime=1623378600
loading_time=5
meter_list=[]
model_time_setup=[60,30,60,90]
###########################################list made and printing function
switch_data_list=[]
job_data_list=[]

def print_switch_data(data):
    for d in data:
        print('time= {} status= {}   {}' .format(d[0],d[1],d[2]))
def print_job_data(data):
    for d in data:
        print('job came {} at =     {}       in machine {}      for product {}   job number = {}' .format(d[2],d[1],d[3],d[0],d[4]))
###########################################
class Model_Factory:
    def __init__(self, env):
        self.env = env
        self.model=[]
        for i in range(len(initial_model_list)):
            self.model.append(simpy.Container(env, capacity = model_capacity, init = initial_model_list[i][1]))
        self.dispatch = simpy.Container(env ,capacity = dispatch_capacity, init = 0)
        self.pre_shaping = simpy.Container(env, capacity = pre_shaped_capacity, init = 0)
        self.pre_planing = simpy.Container(env, capacity = pre_planed_capacity, init = 0)
        self.pre_honing = simpy.Container(env, capacity = pre_honed_capacity, init = 0)
def milling(env, model_factory):
    job=1
    end_m=0
    while True:
        for j in range(len(initial_model_list)) :
            if not j ==0:
                u=env.now
                try:
                    if u <= (breakdown[1][0][0]-model_time_setup[0]) :
                        pass
                    else:
                        print('breakdown while MILLING SETUP, taking timeout',datetime.datetime.fromtimestamp(int(breakdown[1][0][0])).strftime('%Y-%m-%d %H:%M:%S'))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,1)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,1)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,2)))
                        breakdown2[1].append(tuple((env.now,breakdown[1][0][1])))
                        yield env.timeout(breakdown[1][0][1])
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,2)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,1)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,1)))
                        breakdown[1].pop(0)
                except:
                    pass
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),0,2)))
                yield env.timeout(model_time_setup[0])
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),0,2)))
                end_m=env.now
            for i in range(0,initial_model_list[j][1]):
                yield model_factory.model[j].get(1)
                job_data_list.append(tuple((str(initial_model_list[j][0]),datetime.datetime.fromtimestamp(int(env.now)),'IN',1,job)))
                if not end_m==0:
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(end_m)),0,2)))
                else:
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(starttime)),0,2)))
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(starttime)),1,1)))
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now+loading_time)),0,2)))
                yield env.timeout(loading_time)
                u = env.now
                product_time=(product_cycle[(initial_model_list[j][0]-1)][1])
                random_time=int(random.gauss(product_time[0],product_time[1]))
                try:
                    if u <= (breakdown[1][0][0]-random_time) :
                            pass
                    else:
                            print('breakdown while MILLING was running, taking timeout',datetime.datetime.fromtimestamp(int(breakdown[1][0][0])).strftime('%Y-%m-%d %H:%M:%S'))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,1)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,1)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,2)))
                            breakdown2[1].append(tuple((env.now,breakdown[1][0][1])))
                            yield env.timeout(breakdown[1][0][1])
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,2)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,2)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,1)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,1)))
                            breakdown[1].pop(0)
                except:
                    pass
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,2)))
                yield env.timeout(random_time)
                end_m=env.now
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,2)))
                yield model_factory.pre_shaping.put(1)
                job_data_list.append(tuple((str(initial_model_list[j][0]),datetime.datetime.fromtimestamp(int(env.now)),'OUT',1,job)))
                job+=1
def shaping(env, model_factory):
    job=1
    end_m=0
    while True:
        for j in range(len(initial_model_list)):
            if not j ==0:
                u=env.now
                try:
                    if u <= (breakdown[2][0][0]-model_time_setup[1]) :
                            pass
                    else:
                    
                        print('breakdown while SHAPING SETUP, taking timeout',datetime.datetime.fromtimestamp(int(breakdown[2][0][0])).strftime('%Y-%m-%d %H:%M:%S'))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,3)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,3)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,4)))
                        breakdown2[2].append(tuple((env.now,breakdown[2][0][1])))
                        yield env.timeout(breakdown[2][0][1])
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,4)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,3)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,3)))
                        breakdown[2].pop(0)
                except:
                    pass
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),0,4)))
                yield env.timeout(model_time_setup[1])
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),0,4)))
                end_m=env.now
            for i in range(0,initial_model_list[j][1]):
                yield model_factory.pre_shaping.get(1)
                job_data_list.append(tuple((str(initial_model_list[j][0]),datetime.datetime.fromtimestamp(int(env.now)),'IN',2,job)))
                if not end_m==0:
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(end_m)),0,4)))
                else:
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(starttime)),0,4)))
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(starttime)),1,3)))
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now+loading_time)),0,4)))
                yield env.timeout(loading_time)
                u=env.now
                product_time=(product_cycle[(initial_model_list[j][0]-1)][2])#get the mean and deviation
                random_time=int(random.gauss(product_time[0],product_time[1]))#save the random time for the cycle in variable
                try:
                    if u <= (breakdown[2][0][0]-random_time) :
                            pass
                    else:
                            print('breakdown while SHAPING was running, taking timeout',datetime.datetime.fromtimestamp(int(breakdown[2][0][0])).strftime('%Y-%m-%d %H:%M:%S'))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,3)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,3)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,4)))
                            breakdown2[2].append(tuple((env.now,breakdown[2][0][1])))
                            yield env.timeout(breakdown[2][0][1])   
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,4)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,4)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,3)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,3)))
                            breakdown[2].pop(0)
                except:
                    pass
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,4)))
                yield env.timeout(random_time)
                end_m=env.now
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,4)))
                yield model_factory.pre_planing.put(1)
                job_data_list.append(tuple((str(initial_model_list[j][0]),datetime.datetime.fromtimestamp(int(env.now)),'OUT',2,job)))
                job+=1
def planing(env, model_factory):
    job=1
    end_m=0
    while True:
        for j in range(len(initial_model_list)):
            if not j ==0:
                u=env.now
                try:
                    if u <= (breakdown[3][0][0]-model_time_setup[2]) :
                            pass
                    else:
                    
                        print('breakdown while PLANING SETUP, taking timeout',datetime.datetime.fromtimestamp(int(breakdown[3][0][0])).strftime('%Y-%m-%d %H:%M:%S'))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,6)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,6)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,7)))
                        breakdown2[3].append(tuple((env.now,breakdown[3][0][1])))
                        yield env.timeout(breakdown[3][0][1])
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,7)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,6)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,6)))
                        breakdown[3].pop(0)
                        print(env.now)
                except:
                    pass
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),0,7)))
                yield env.timeout(model_time_setup[2])
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),0,7)))
                end_m=env.now
            for i in range(0,initial_model_list[j][1]):
                yield model_factory.pre_planing.get(1)
                job_data_list.append(tuple((str(initial_model_list[j][0]),datetime.datetime.fromtimestamp(int(env.now)).strftime('%Y-%m-%d %H:%M:%S'),'IN',3,job)))
                if not end_m==0:
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(end_m)),0,7)))
                else:
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(starttime)),0,7)))
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(starttime)),1,6)))
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now+loading_time)),0,7)))
                yield env.timeout(loading_time)
                u=env.now
                product_time=(product_cycle[(initial_model_list[j][0]-1)][3])#get the mean and deviation
                random_time=int(random.gauss(product_time[0],product_time[1]))#save the random time for the cycle in variable
                try:
                    if u <= (breakdown[3][0][0]-random_time) :
                            pass
                    else:
                            print('breakdown while PLANING was running, taking timeout',datetime.datetime.fromtimestamp(int(breakdown[3][0][0])).strftime('%Y-%m-%d %H:%M:%S'))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,6)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,6)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,7)))
                            breakdown2[3].append(tuple((env.now,breakdown[3][0][1])))
                            yield env.timeout(breakdown[3][0][1])
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,7)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,7)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,6)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,6)))
                            breakdown[3].pop(0)
                except:
                    pass
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,7)))
                yield env.timeout(random_time)
                end_m=env.now   
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,7)))
                yield model_factory.pre_honing.put(1)
                job_data_list.append(tuple((str(initial_model_list[j][0]),datetime.datetime.fromtimestamp(int(env.now)).strftime('%Y-%m-%d %H:%M:%S'),'OUT',3,job)))
                job+=1
def honing(env, model_factory):
    job=1
    end_m=0
    while True:
        for j in range(len(initial_model_list)):
            if not j ==0:
                u=env.now
                try:
                    if u <= (breakdown[4][0][0]-model_time_setup[3]) :
                            pass
                    else:
                    
                        print('breakdown while HONING SETUP, taking timeout',datetime.datetime.fromtimestamp(int(breakdown[4][0][0])).strftime('%Y-%m-%d %H:%M:%S'))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,8)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,8)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,9)))
                        breakdown2[4].append(tuple((env.now,breakdown[4][0][1])))
                        yield env.timeout(breakdown[4][0][1])
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,9)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,8)))
                        switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,8)))
                        breakdown[4].pop(0)
                except:
                    pass
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),0,9)))
                yield env.timeout(model_time_setup[3])
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),0,9)))
                end_m=env.now
            for i in range(0,initial_model_list[j][1]):
                yield model_factory.pre_honing.get(1)
                job_data_list.append(tuple((str(initial_model_list[j][0]),datetime.datetime.fromtimestamp(int(env.now)),'IN',4,job)))
                if not end_m==0:
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(end_m)),0,9)))
                else:
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(starttime)),0,9)))
                    switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(starttime)),1,8)))
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now+loading_time)),0,9)))
                yield env.timeout(loading_time)
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,9)))
                u=env.now
                product_time=(product_cycle[(initial_model_list[j][0]-1)][3])#get the mean and deviation
                random_time=int(random.gauss(product_time[0],product_time[1]))#save the random time for the cycle in variable
                try:
                    if u <= (breakdown[4][0][0]-random_time) :
                            pass
                    else:
                            print('breakdown while HONING was running, taking timeout',datetime.datetime.fromtimestamp(int(breakdown[4][0][0])).strftime('%Y-%m-%d %H:%M:%S'))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,8)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,8)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,9)))
                            breakdown2[4].append(tuple((env.now,breakdown[4][0][1])))
                            yield env.timeout(breakdown[4][0][1])
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,9)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),2,8)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,9)))
                            switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,8)))
                            breakdown[4].pop(0)
                except:
                    pass
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,9)))
                yield env.timeout(random_time)
                end_m=env.now
                switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(env.now)),1,9)))
                yield model_factory.dispatch.put(1)
                job_data_list.append(tuple((str(initial_model_list[j][0]),datetime.datetime.fromtimestamp(int(env.now)),'OUT',4,job)))
                job+=1
env = simpy.Environment(starttime)
model_factory = Model_Factory(env)
milling_process = env.process(milling(env, model_factory))
shaping_process = env.process(shaping(env, model_factory))
planing_process = env.process(planing(env, model_factory))
honing_process = env.process(honing(env, model_factory))
env.run(until = endtime)
switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(seconds)),1,1)))
switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(seconds)),1,3)))
switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(seconds)),1,6)))
switch_data_list.append(tuple((datetime.datetime.fromtimestamp(int(seconds)),1,8)))
def insert_switch_data():
    with psycopg2.connect(CONNECTION) as conn:
        query = """INSERT INTO switch_data (time, status, switch_id) VALUES (%s, %s, %s)"""
        cursor = conn.cursor()
        cursor.executemany(query, switch_data_list)
        conn.commit()
        cursor.close()
        print('done')
insert_switch_data()
def insert_job_data():
    with psycopg2.connect(CONNECTION) as conn:
        query = """INSERT INTO job_data (product_id ,time, status, machine_id, job_no) VALUES (%s, %s, %s, %s, %s)"""
        cursor = conn.cursor()
        cursor.executemany(query, job_data_list)
        conn.commit()
        cursor.close()
        print('done')
insert_job_data()
def meter_data_populate():
    j=starttime
    for i in range(starttime,endtime):
        while j<=endtime:
            try:
                if j==breakdown2[1][0][0]:
                    for i in range(breakdown2[1][0][1]):
                        meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j+i)),1,np.random.randint(0, 1))))
                        meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j+i)),2,np.random.randint(10, 15))))
                    j=j+breakdown2[1][0][1]
                    breakdown2[1].pop(0)
                else:
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),1,np.random.randint(0, 8))))
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),2,np.random.randint(17, 85))))
                    j+=1
            except:
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),1,np.random.randint(0, 8))))
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),2,np.random.randint(17, 85))))
                    j+=1


    j=starttime
    for i in range(starttime,endtime):
        while j<=endtime:
            try:
                if j==breakdown2[2][0][0]:
                    for i in range(breakdown2[2][0][1]):
                        meter_list.append(tuple((datetime.datetime.fromtimestamp(int(i+j)),3,np.random.randint(0, 2))))
                        meter_list.append(tuple((datetime.datetime.fromtimestamp(int(i+j)),4,np.random.randint(10,15))))
                    j=j+breakdown2[2][0][1]
                    breakdown2[2].pop(0)
                else:
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),3,np.random.randint(2, 7))))
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),4,np.random.randint(17, 65))))
                    j+=1
            except:
                meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),3,np.random.randint(2, 7))))
                meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),4,np.random.randint(17, 65))))
                j+=1

    j=starttime
    for i in range(starttime,endtime):
        while j<=endtime:
            try:
                if j==breakdown2[3][0][0]:
                    for i in range(breakdown2[3][0][1]):
                        meter_list.append(tuple((datetime.datetime.fromtimestamp(int(i+j)),5,np.random.randint(0, 2))))
                    j=j+breakdown2[3][0][1]
                    breakdown2[3].pop(0)
                else:
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),5,np.random.randint(1, 8))))    
                    j+=1     
            except:
                meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),5,np.random.randint(1, 8))))
                j+=1

    j=starttime
    for i in range(starttime,endtime):
        while j<=endtime:
            try:
                if j==breakdown2[4][0][0]:
                    for i in range(breakdown2[4][0][1]):
                        meter_list.append(tuple((datetime.datetime.fromtimestamp(int(i+j)),6,np.random.randint(0, 1))))
                        meter_list.append(tuple((datetime.datetime.fromtimestamp(int(i+j)),7,np.random.randint(10, 15))))
                        meter_list.append(tuple((datetime.datetime.fromtimestamp(int(i+j)),8,np.random.randint(1, 3))))
                    j=j+breakdown2[4][0][1]
                    breakdown2[4].pop(0)
                else:
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),6,np.random.randint(0, 12))))
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),7,np.random.randint(15, 85))))
                    meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),8,np.random.randint(4, 9))))
                    j+=1
            except:
                meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),6,np.random.randint(0, 12))))
                meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),7,np.random.randint(15, 85))))
                meter_list.append(tuple((datetime.datetime.fromtimestamp(int(j)),8,np.random.randint(4, 9))))
                j+=1
meter_data_populate()
def insert_meter_data():
    with psycopg2.connect(CONNECTION) as conn:
        query = """INSERT INTO  metre_data (time, metre_id, reading) VALUES (%s, %s, %s)"""
        cursor = conn.cursor()
        cursor.executemany(query, meter_list)
        conn.commit()
        cursor.close()
        print('done')
insert_meter_data()
# print('---------------------------------------------------------------------')
# print(f'pre shaped %d models ready to go!' % model_factory.pre_shaping.level)
# print(f'pre planed %d models ready to go!' % model_factory.pre_planing.level)
# print(f'pre honed %d models ready to go!' % model_factory.pre_honing.level)
# print(f'Dispatch has %d models ready to go!' % model_factory.dispatch.level)
# print('---------------------------------------------------------------------')
# print('                       MILLING MACHINE ')
# print_switch_data(milling_list)
# print('---------------------------------------------------------------------')
# print('                       SHAPING MACHINE ')
# print_switch_data(shaping_list)
# print('---------------------------------------------------------------------')
# print('                       PLANING MACHINE ')
# print_switch_data(planing_list)
# print('---------------------------------------------------------------------')
# print('                       HONING MACHINE ')
# print_switch_data(honing_list)
# print('---------------------------------------------------------------------')
# print(switch_data_list)
# print_job_data(job_data_list)
# print(job_data_list)