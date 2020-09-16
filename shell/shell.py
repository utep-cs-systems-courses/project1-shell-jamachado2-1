import os, sys, time, re

while True:
    pid = os.getpid()

    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode)
    else:
        os.write(1, ('$ ').encode())
        try:
            command = [str(n) for n in input().split()]
        except EOFError:
            sys.exit(1)

    if 'cd' in command:
        try:
            os.chdir(command[1])
        except FileNotFoundError:
            pass
        continue

    def path(args):
        for dir in re.split(":", os.environ['PATH']): # Try each directory in the path
            program = "%s%s" % (dir, args[0])
            os.write(1, ("Child: ...trying to excec %s\n" % program).encode())
            try:
                os.execve(program, args, os.environ)  # Try to exec program
            except FileNotFoundError:
                pass                                  # fail quitely

            os.write(2, (f"{args[0]}: command nor found.").encode())
            sys.exit(1)                               # terminate with error

    def execute(command):
        rc = os.fork()                                # create child project
        args = command.copy()

        if '&' in args:
            args.remove('&')
        if 'exit' in args:
            os.write(1, ("Process finished."))
            sys.exit(0)
        if '' in args:
            pass

        if rc < 0:                        # fork failed
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            if '>' in args:
                os.close(1)
                os.open(args[-1], os.O_CREAT | os.O_WRONGLY);
                os.set_inheritable(1, True)

                arg = arg[0:args.index(">")]
                path(arg)

            if '<' in args:
                os.close(0)
                os.open(args[-1], os.O_RDONLY);
                os.set_inheritable(0, True)

            if '|' in args:
                args = ' '.join([str(elem) for elem in args])
                pipe = args.split("|")
                p1 = pipe[0].split()
                p2 = pipe[1].split()

                # file desciptors for reading and writing
                pr, pw = os.pipe()
                for f in (pr, pw):
                    os.set_inheritable(f, True)

                pf = os.fork()

                if pf < 0:       # pf failed
                    os.write(2, ("pipe fork failed").encode())
                    sys.exit(1)
                elif pf == 0:    # child process
                    os.close(1)
                    os.dup(pw)   # fd1 to pipe
                    os.set_inheritable(1, True)
                    for fd in (pr, pw):
                        os.close(fd)
                    path(p1)
                else:
                    os.close(0)
                    os.dup(pr)
                    os.set_inheritable(0, True)
                    for fd in (pw, pr):
                        os.close(fd)
                    path(p2)
            else:
                path(args)

        else:
            if not '&' in command:
                os.write(1, ("Parent: My pid=%d. child;s pid=%d\n" % (pid,rc)).encode())
                childPidCode = os.wait()
                os.write(1, ("Parent: chidl %d terminated with exit code %d\n" % childPidCode).encode())

    if not command:
        pass
    else:
        execute(command)
