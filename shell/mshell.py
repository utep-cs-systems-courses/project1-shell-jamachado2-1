#! /usr/bin/env python3

import os, sys, time, re

#export PS1 = \\u@\\h

commands = ["cd","ls","..",">","<","|","exit"]

def change_dir(args):                        
    cwd = os.getcwd()                      # return the current working directory of a process
    args, directory = re.split(" ", args)
    if os.path.isdir(cwd + "/" + args[0]): # check if the directory exist
        os.chdir(cwd + "/" + args[0])
        
def list_dir():                             
    cwd = os.getcwd()
    directories = os.listdir()               # return a list of the entries in the directory
    for d in directories:                    # loop over the directories
        print(d, end=" ")                    # print the content 
    print("\n")
    
def path(args):
    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
        program = "%s%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)  # try to exec program
        except FileNotFoundError:                 # expected
            pass                                  # fail quitely
    #os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
    sys.exit(1)                               # terminate with error

def redirectory_out_in(user_input, out_in):
    user_input = user_input.split(out_in)
    # Output redirection
    if out_in == ">":    
        os.close(1)                          # redirect child's stdout
        os.open(user_input[0].strip(), os.O_CREAT | os.O_WRONLY);
        os.set_inheritable(1, True)
        path(user_input[0].split())
    # Input redirection
    else: 
        os.close(0)                          # redirect child's stdin
        os.open(user_input[0], os.O_CREAT | os.O_RDONLY);
        os.set_inheritable(0, True)
        path(user_input[0].split())
        

if __name__ == '__main__':
    
    while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode)
        else:
            os.write(1, ("$ ").encode())
            try:
                user_input = input()
            except EOFError:
                sys.exit(1)


        # Add your commands here ..
        if "" in user_input:
            pass                # keep running if user enters no command
        if user_input == "exit":
            os.write(1, ("Process finished.\n").encode())
            sys.exit(0)
        if "cd" in user_input:
            change_dir(user_input)
        if "ls" in user_input:
            list_dir()
        if ">" in user_input:
            redirectory_out_in(">", user_input)
        if "<" in user_input:
            redirectory_out_in("<", user_input)

            
        pid = os.getpid()
        # About to fork
        rc = os.fork()

        if rc < 0:
            # fork failed
            sys.exit(1)
        elif rc == 0:
            args = user_input.split()


            # using pipes
            if user_input == "|":
                p = user_input.split("|")
                pipe1 = p[0].split()
                pipe2 = p[1].split()
    
                # Reading and writing pipe
                pr,pw = os.pipe()
                for f in (pr, pw):
                    os.set_inheritable(f, True)

                # Forking child
                pf = os.fork()
                if pf < 0:
                    # fork failed, returning
                    sys.exit(1)
                if pf == 0:
                    os.close(1)
                    os.dup(pw)                  # redirect childs stdout
                    os.set_inheritable(1, True)

                    for fd in (pr, pw):
                        os.close(fd)
                    path(pipe1)
                else:                           # parent fork
                    os.close(0)
                    os.dup(pr)
                    os.set_inheritable(0, True)
                    for fd in (pw, pr):
                        os.close(fd)
                    path(pipe2)


        else:                               # parent forked ook
                childPidCode = os.wait()
