#! /usr/bin/env python3

import os, sys, time, re

#export PS1 = \\u@\\h

commands = ["cd", "ls", "..", ">", "exit"]


# probably this doesn;t work because I cannot get right the 'PS1'?
def change_dir(args):                        
    cwd = os.getcwd()                        # return the current working directory of a process
    args, directory = re.split(" ", args)
    if os.path.isdir(cwd + "/" + directory): # check if the directory exist
        os.chdir(cwd + "/" + directory)

def list_dir():                             
    cwd = os.getcwd()
    directories = os.listdir()               # return a list of the entries in the directory
    for d in directories:                    # loop over the directories
        print(d, end=" ")                    # print the content 
    print("\n")
    
def path(args):
    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
        args = ["wc", "mshell.py"]
        program = "%s%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)  # try to exec program
            childPidCode = os.wait()
        except FileNotFoundError:                 # expected
            pass                                  # fail quitely
        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                               # terminate with error

def redirectory(args):
    
    user_input = input.split(args)
    # Output redirection
    if args == ">":
        
        os.close(1)                 # redirect child's stdout
        os.open("mshell-output.txt", os.O_CREAT | os.O_WRONLY);
        os.set_inheritable(1, True)
        path(user_input[0].split())
        
    # Input redirection
    else: 
        os.close(0)                 # redirect child's stdin
        os.open("mshell-input.txt", os.O_CREAT | os.O_RDONLY);
        os.set_inheritable(os, True)
        path(user_input[0].split())

# how to pipe
# it's kinda similar to redirectory, but with dup()
#def pipes(args):
    

def execute(args):
    if user_input == "":
        pass
    elif user_input == "exit":
        os.write(1, ("Process finished.\n").encode())
        sys.exit(1)
    elif user_input == "cd":
        change_dir(args)
    elif user_input == "ls":
        list_dir()
    elif user_input == ">":
        redirectory(args)
    elif user_input == "<":
        redirectory(args)
    #elif args not in commands:
    #    print(args + ": command not valid")
    #else:
    #    print("valid command")

        
while True:
    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode)
    else:
        os.write(1, ("$ ").encode())
        try:
            user_input = input()
            execute(user_input)
        except EOFError:
            sys.exit(1)
        
pid = os.getpid()
os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
rc = os.fork()

if rc < 0:
    os.write(2, ("fork failed, returning %d\n" % rc).encode())
    sys.exit(1)
elif rc == 0:              # child
    os.write(1, ("Child: My pid==%d. Parent's pid=%d\n" % (os.getpid(),pid)).encode())
    args = ["wc", user_input[1]]

else:                                            # parent (forked ok)
    os.write(1, ("Parent: My pid=%d.   Child's pid=%d\n" % (pid, rc)).encode())        
    childPidCode = os.wait()
    os.write(1, ("Parent: child %d terminated with exit code %d\n" % childPidCode).encode())
