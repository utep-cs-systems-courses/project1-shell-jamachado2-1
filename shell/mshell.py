#! /usr/bin/env python3

import os, sys, time, re

#export PS1 = \\u@\\h

commands = ["cd", "ls", "..", "exit"]

while True:
    prompt = input("$ ")
    
    if prompt == "exit":
        sys.exit(1)
    elif prompt not in commands:
        print(prompt + ": command not valid")
    else:
        print("valid command")
    
user_in = prompt.split()
pid = os.getpid()
rc = os.fork()
args = ["wc",user_in[1]]


if rc < 0:
    os.write(2, ("fork failed, returning %d\n" % rc).encode())
    sys.exit(1)
elif rc == 0:
    os.write(1, ("Child: My pid==%d. Parent's pid=%d\n" % (os.getpid(),pid)).encode())

    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
        program = "%s%s" % (dir, args[0])
        try:
            # change the exec to run our commands
            os.execve(program, args, os.environ) # try to exec program
            childPidCode = os.wait()
        except FileNotFoundError:                # expected
            pass                                 # fail quitely
        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

else:                                            # parent (forked ok)
    os.write(1, ("Parent: My pid=%d.   Child's pid=%d\n" %
                 (pid, rc)).encode())        
