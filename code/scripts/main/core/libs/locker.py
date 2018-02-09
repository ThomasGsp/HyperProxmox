import os

class Locker:
    def createlock(self, lockfile, position, date=0):
        try:
            if os.path.exists(lockfile):
                f = open(lockfile, "r+")
                return f.read()
            else:
                f = open(lockfile, "w")
                f.write(str(date))
        except BaseException as e:
            raise("Can't create or read the lock file: {0}".format(e))

    def unlock(self, lockfile, position):
        try:
            os.remove(lockfile)
        except BaseException as e:
            if position != "startup":
                print("Can't delete the lock file: {0}".format(e))