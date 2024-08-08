#!/usr/bin/env python3.12
import argparse
from functions import *
from prompts import *

#pour test API mistral



def main():

    print(ascii_art)
    print(intruder_man)
    parser = argparse.ArgumentParser(description='input output')
    parser.add_argument("session_name", type=str, help='Give da pentest session a name')
    args = parser.parse_args()
    session_name = args.session_name
    ip_addr = ''

    #while True:
    #    ip_addr = input("Entrez l'address IP de la  machine : ")
    #    if is_it_anIP(ip_addr.strip()) or ip_addr.strip() == 'localhost':
    #        break
    

    while True:
        try:

            
            task = input("Pentest-AI>")
            if (len(task.split()) == 0):
                continue
            add_task(task)
            if task.strip().upper() in BUILDIN_COMMAND:
                print(f"{Colors.AI_OUTPUT}{buidling_command(task.strip().upper(), session_name)}{Colors.RESET}")
            else:
                start_task(task, session_name)
            
        except KeyboardInterrupt:
            sys.exit()

if __name__ == '__main__':
    main()
