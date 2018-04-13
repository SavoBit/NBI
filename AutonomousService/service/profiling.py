import cProfile
import pstats
import io
import logging
import os
import time

PROFILE_LIMIT = int(os.environ.get("PROFILE_LIMIT", 5))
PROFILER = bool(int(os.environ.get("PROFILER", 1)))


def profiler_enable(worker, req):
    worker.profile = cProfile.Profile()
    worker.profile.enable()


def profiler_summary(worker, req, total_time):
    s = io.StringIO()
    worker.profile.disable()
    ps = pstats.Stats(worker.profile, stream=s)

    # Only the the functions from resources and requester will be measured and limited to 5
    # the total amount of time presented is related to the worker time
    ps.sort_stats('cumtime').print_stats('(resources|requester)', PROFILE_LIMIT)

    logger = logging.getLogger('Profiling')
    logger.info("Time: %.3f Method: [%s] URI: %s\n%s" % (total_time, req.method, req.uri, s.getvalue()))


def pre_request(worker, req):
    worker.start_time = time.time()
    if PROFILER is True:
        profiler_enable(worker, req)


def post_request(worker, req, *args):
    total_time = time.time() - worker.start_time
    if PROFILER is True:
        profiler_summary(worker, req, total_time)
