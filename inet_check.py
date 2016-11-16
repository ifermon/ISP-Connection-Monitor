import pyping
import time
import datetime

HOSTS = ['google.com', '209.18.47.61', '209.18.47.62']
DT_FORMAT_STR = "%a %b %d %Y %I:%M:%S %p"
TIMEOUT = 350.0 # Time to wait for ping to return

def now(): return datetime.datetime.now()

def duration_str(td):
    # Assumes we will never have a difference less than a second, true for ping
    d = 0
    h = 0
    # Takes a time delta and returns in terms of xx days yy hours mm minutes ss seconds
    m, s = divmod(td.total_seconds(), 60) # Get seconds and minutes
    if m > 60: 
        # We are into hours
        h, m = divmod(m, 60)
        if h > 24:
            # We are into days
            d, h = divmod(h, 24)

    # Now build the string
    ret_str = "{:2.0f} seconds".format(s)
    if m != 0:
        ret_str = "{:2.0f} minutes {}".format(m, ret_str)
        if h != 0:
            ret_str = "{:2.0f} hours {}".format(h, ret_str)
            if d != 0:
                ret_str = "{:10.0f} days {}".format(d, ret_str)
    return ret_str
    


class Avail(object):
    def __init__(self, name):
        self._name = name
        self._active = True
        self._start_of_downtime = None

    def set_active(self, state):
        if self._active == True and state == False:
            # Connection was up, now it's down
            self._start_of_downtime = now()
            self._active = False
        elif self._active == state: # Either true true or false false
            # Do nothing
            pass
        elif self._active == False and state == True:
            # Connection came back up, print msg about outage
            self._active = state
            dt_from = self._start_of_downtime
            dt_to = now()
            dt_duration = duration_str(dt_to - dt_from)
            dt_from = dt_from.strftime(DT_FORMAT_STR)
            dt_to = dt_to.strftime(DT_FORMAT_STR)
            print("Host '{}' was down for {} seconds from {} to {}".format(self._name, dt_duration, dt_from, dt_to))
        else:
            raise TypeError("Invalid state status, should be boolean")
        return

    def get_host(self): return self._name
    def __str__(self): return self._name

# Log that we are starting
print("Starting connection monitoring {}".format(now().strftime(DT_FORMAT_STR)))

# Create the list of hosts
hl = {}
for h in HOSTS:
    hl[h] = Avail(h)

# Loop through each host, pinging, and print out when we have an outage
while True:
    for h in hl.values():
        try:
            r = pyping.ping(h.get_host(), timeout=TIMEOUT)
        except:
            print("Got error for host: {}".format(h.get_host()))
        if r.avg_rtt == None:
            # This happens sometimes when first started
            #print("Continuing for {}".format(h))
            continue
        else:
            avg_rtt = float(r.avg_rtt)
        #print("Pinged {} with round trip time of {}".format(h, avg_rtt))
        if avg_rtt > TIMEOUT:
            h.set_active(False)
            #print("set {} as inactive".format(h))
        else:
            h.set_active(True)
            #print("set {} as active".format(h))
    time.sleep(5)
