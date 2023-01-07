import psycopg2
from pgcopy import CopyManager

CONNECTION = "postgres://postgres:nitin@localhost:5432/timeseries"

conn = psycopg2.connect(CONNECTION)

# insert using pgcopy
def fast_insert(conn):
    cursor = conn.cursor()

    # for sensors with ids 1-4
    for id in range(1, 4, 1):
        data = (id,)
        # create random data
        simulate_query = """SELECT generate_series(now() - interval '24 hour', now(), interval '5 minute') AS time,
                           %s as sensor_id,
                           random()*100 AS temperature,
                           random() AS cpu
                        """
        cursor.execute(simulate_query, data)
        values = cursor.fetchall()

        # column names of the table you're inserting into
        cols = ['time', 'sensor_id', 'temperature', 'cpu']

        # create copy manager with the target table and insert
        mgr = CopyManager(conn, 'sensor_data', cols)
        mgr.copy(values)

    # commit after all sensor data is inserted
    # could also commit after each sensor insert is done
    fast_insert()
    conn.commit()