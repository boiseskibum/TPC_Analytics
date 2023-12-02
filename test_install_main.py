# Main program

######################################################################
# debuggging and logging
from share import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

log.msg(f'INFO - Valid logging levels are: {util.logging_levels}')
log.set_logging_level("WARNING")  # this will show errors but not files actually processed

log.msg(f'ending, thats all folks')

