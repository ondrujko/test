import os
import subprocess
import sys

filename = 'bot.py'
while True:
    try:

        p = subprocess.Popen('python '+filename, shell=True).wait()
        
        if p != 0:
            continue
        else:
            os.execv(__file__, sys.argv)
    except Exception as e:
        print(e)