import ntplib
import time

def sync_time(ntp_server='pool.ntp.org'):

    c = ntplib.NTPClient()
    response = c.request(ntp_server)
    offset = response.offset

    original_timestamp = time.time
    def correct_time():
        return original_timestamp() + offset

    time.time = correct_time
