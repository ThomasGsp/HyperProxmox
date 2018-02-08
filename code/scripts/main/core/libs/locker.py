import os

class locker:
    def createlock(self, lockfile, date=0):
        try:
            if os.path.exists(lockfile):
                f = open(lockfile, "r+")
                return f.read()
            else:
                f = open(lockfile, "w")
                f.write(date)
        except BaseException as e:
            raise("Can't create or read the lock file: {0}".format(e))

    def unlock(self, lockfile):
        try:
            os.remove(lockfile)
        except BaseException as e:
            raise ("Can't delete the lock file: {0}".format(e))