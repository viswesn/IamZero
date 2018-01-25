import time
import calendar
import pdb
import sched
from rclone import *
from gcal import *
from util import *
from datetime import datetime

gcalendar_id = "gdmhdc1p72eqsgme87cb77m8d8@group.calendar.google.com"
rclone_sched = sched.scheduler(time.time, time.sleep)
RCLONE_EVENT_TIMER = 60 * 5 # for 5 min
RCLONE_EXE = "C://rclone//rclone.exe"
RCLONE_REMOTE = "Gdrive:"

def get_event_timer_offset(g_event_time):
    g_time = time.strptime(g_event_time, "%Y-%m-%dT%H:%M:%S+05:30")
    g_ctime = calendar.timegm(g_time)

    now_time = datetime.now()
    now_ctime = calendar.timegm(now_time.timetuple())

    """
    nowUTCTime = datetime.datetime.utcnow()
    nowUTCCtime = calendar.timegm(nowUTCTime.timetuple())
    timeOffSet1 = gCEventTime - nowUTCCtime
    """

    time_off_set = g_ctime - now_ctime
    return time_off_set


def convert_path(path):
    return path.replace('\\', '//')


def do_rclone(gcal, action):
    print "Starting z{} now".format(action)
    index = 0
    dry_run = True
    paths = gcal.get_backup_paths()
    result = list()
    lpaths = list()

    for path in paths:
        if len(path) == 0:
            break
        index = index + 1
        lpath = dict()
        logfile = str_join("rclone_",
                           datetime.now().strftime("%Y%m%d-%H%M%S"),
                           ".log")
        if action == "Recover":
            (drive_path, local_path) = (
                (convert_path(path)).strip()).split(':', 1)
            execute = str_join(RCLONE_EXE, " sync"
                               " \"{}{}\"".format(RCLONE_REMOTE, drive_path),
                               " \"{}\"".format(local_path),
                               " -v --log-file {}".format(logfile))
        else:
            (local_path, drive_path) = (
                (convert_path(path)).strip()).rsplit(':', 1)
            execute = str_join(RCLONE_EXE, " sync"
                               " \"{}\"".format(local_path),
                               " \"{}{}\"".format(RCLONE_REMOTE, drive_path),
                               " -v --log-file {}".format(logfile))

        lpath['path'] = local_path
        lpath['log'] = logfile
        lpaths.append(lpath)
        if dry_run:
            execute = str_join(execute, " --dry-run")
        cmd(execute)

    errors = 0
    index = 0
    for lpath in lpaths:
        index = index + 1
        log_fname = lpath.get("log")
        if log_fname and os.path.isfile(log_fname):
            dresult = get_rclone_log_details(log_fname)
            dresult['path'] = lpath.get("path", "")
            errors = errors + int(dresult.get("Errors"))
            result.append(dresult)
            # os.unlink(log_fname)

    print "z{} completed for event {}".format(action, gcal.event_id)
    gcal.update_gevent(result, errors)


def do_gcal_check(job=None):
    global gcalendar_id
    gcal = GCalendar(gcalendar_id)
    while (True):
        print "Checking Google Calendar zBackUp Event"
        # schedule this function to run after 5 mim
        g_next_event= gcal.get_next_gevent(gcalendar_id)

        # There were no backup events scheduled
        if g_next_event == dict():
            return

        gevent_id = g_next_event.get("eventId", None)
        start_tm = g_next_event.get("start_tm", None)
        action = g_next_event.get("action", None)
        event_timer_offset = get_event_timer_offset(start_tm)

        print "Found Google Calendar event: " + gevent_id
        print "Starting time of the event : " + start_tm
        print "Event will start in " + str(event_timer_offset) + "min"
        rclone_sched.enter(2, 1, do_rclone, (gcal, action))
        rclone_sched.run()
        if event_timer_offset < RCLONE_EVENT_TIMER:
            """
            If event needs to be done in 5 min then block and wait
            for it to complete
            """
            print "Event waiting for to run"
            rclone_sched.enter(5, 1, do_rclone_backup, (gcal, ))
            rclone_sched.run()
        time.sleep(RCLONE_EVENT_TIMER)


if __name__ == "__main__":
    try:
        do_gcal_check()
    except (KeyboardInterrupt, SystemExit):
        exit(0)