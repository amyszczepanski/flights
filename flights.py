import socket
import sqlite3
import signal
import errno

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('10.0.1.15', 30003))
s.sendall('Hello, world')

# Catches SIGINT and SIGTERM and closes connections
# https://stackoverflow.com/a/31464349
class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    
    def exit_gracefully(self, signum, frame):
        self.kill_now = True

killer = GracefulKiller()

# My database
conn = sqlite3.connect('flights.db')
c = conn.cursor()

# Every time the counter gets big enough, do some housekeeping
thecount = 0

# Reads the lines from the piaware and saves some in the database
while True:
    line = ""

    while True:
        try:
            mychar = s.recv(1)
        except socket.error as (code, msg):
            if code != errno.EINTR:
                print "Well, this is unexpected."
                raise
            else: 
                killer.kill_now = True
        if mychar == "\r":
            try:
                mynewchar = s.recv(1)
            except socket.error as (code, msg):
                if code != errno.EINTR:
                    print "Well, this is unexpected."
                    raise
                else:
                    killer.kill_now = True
            if mynewchar == "\n":
                break
        else:
            line += mychar

    mylist = line.split(',')

    if len(mylist) > 15 \
    and mylist[1] == '3' \
    and mylist[11] != '' \
    and mylist[14] != '' \
    and mylist[15] != '' \
    and int(mylist[11]) > 25000 \
    and float(mylist[14]) > 32.526950 \
    and float(mylist[14]) < 33.524789 \
    and float(mylist[15]) > -117.75 \
    and float(mylist[15]) < -116.078970:
        myrow = (mylist[4], mylist[11], mylist[14], mylist[15])
        c.execute('INSERT INTO positions ( \
        hexcode, altitude, latitude, longitude \
        ) \
        VALUES (?,?,?,?)', myrow)
        thecount += 1
        if thecount % 100 == 0:
            if thecount == 100000:
                c.execute("DELETE FROM positions WHERE observed \
                <= DATETIME('NOW', '-14 day');")
                thecount = 0
            conn.commit()
    if killer.kill_now:
        break

# These run if we get SIGINT or SIGTERM
conn.commit()        
conn.close()
s.close()