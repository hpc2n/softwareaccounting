import ctypes
import ctypes.util
import errno
import os


libc_so = ctypes.util.find_library('c')
libc = ctypes.CDLL(libc_so, use_errno=True)

import logging
logger = logging.getLogger(__name__)


def setfsuid(fsuid):
    """Set user identity used for filesystem checks. See setfsuid(2)."""
    # Per the BUGS section in setfsuid(2), you can't really tell if a
    # setfsuid call succeeded. As a hack, we can rely on the fact that
    # setfsuid returns the previous fsuid and call it twice. The result
    # of the second call should be the desired fsuid.
    libc.setfsuid(ctypes.c_int(fsuid))
    new_fsuid = libc.setfsuid(ctypes.c_int(fsuid))

    print("fsuid: %d" % new_fsuid)
    logger.debug("New fsuid: %d", new_fsuid)

    # Fake an EPERM even if errno was not set when we can detect that
    # setfsuid failed.
    err = errno.EPERM if new_fsuid != fsuid else ctypes.get_errno()
    if err:
        raise OSError(err, os.strerror(err))