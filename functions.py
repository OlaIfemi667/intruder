

import subprocess
import json
from prompts import *

import os, sys
from mistralai.exceptions import MistralException
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import shlex

import ipaddress


API_KEY = "tAjecZNYTo0nyGH6sLdaKFTi6UxWDH6z"
MISTRAL_CLIENT = MistralClient(api_key=API_KEY)

history_chat = []

BUILDIN_COMMAND ={
    "/RESUME",
    "/QUIT",
    "/ASK",
    "/TERMINAL"
}

#pour décorer le code
class Colors:
    USER_INPUT = '\033[94m'  # Blue
    AI_OUTPUT = '\033[92m'   # Green
    OS_OUTPUT = '\033[93m'   # Yellow
    OTHER_OUTPUT ='\033[91m'
    RESET = '\033[0m'  

def load_history(session_name):
    history_file = f"logs/{session_name}.json"
    if not os.path.exists(history_file):
        return []
    with open(history_file, "r") as file:
        return json.load(file)


def buidling_command(command, session_name):
    global history_chat
    if(command == "/ASK"):
        question = input("Ask any thing you want :)  >   ")
        output = ask_mistral("You are an assistant.", question)
        return output
    if(command == "/RESUME"):
        history = load_history(session_name)
        client = MistralClient(api_key=API_KEY)
        AI_ANALYSE = f"""
        You are a cybersecurity expert assisting me during my pentest session. Your task is to analyze my terminal input and output during the reconnaissance phase and provide directives.
        Here is the history of conversation between You an I {history}. Do an resume of the main information we discovered and main task we did. Be ask well as you can but be concise and precise"""

        chat_response = client.chat(
            model="mistral-small",
            messages=[ChatMessage(role="system", content=AI_ANALYSE), ChatMessage(role="user", content="do resume with all important information discovered in a well structure test")]
        )
        return chat_response.choices[0].message.content
    if (command == "/QUIT"):
        print(f"\n\n\n{Colors.OTHER_OUTPUT}Byeeeee :){Colors.RESET}")
        sys.exit()
    if (command == "/TERMINAL"):
        while True:
            try:
                command = input("\n\tintruder-term > ")
                if (len(command.split()) == 0 ):
                    continue
                command_output = execute_action(command)
                history_chat.append({"role": "tool", "content": f"{command} output : {command_output}"})
                save_history(session_name)
            except KeyboardInterrupt:
                break

        


def is_it_anIP(ipaddr):
    try:
        ipaddress.ip_address(ipaddr)
        return True
    except ValueError:
        return False



def ask_mistral(prompt, task):
    global chat_history, API_KEY 
    model = "mistral-large-latest"

    question = task
    chat_history.append({"role" : "user", "content" :question})


    client = MistralClient(api_key=API_KEY)

    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="system", content=prompt), ChatMessage(role="user", content=question)]
    )
    

    return chat_response.choices[0].message.content

def start_task(task, session_name):
    global chat_history, history_chat
    chat_history = []
    print("Thinking")
    try:
        while True:

            try:
                output = generate_path_for_task(task)
                if include_command(output):
                    output = extract_command(output)
                    print(f"{Colors.USER_INPUT}Trying to execute: {output}{Colors.RESET}")
                    command_output = execute_action(output)
                    chat_history.append({"role": "tool", "content": f"{output} output : {command_output}"})
                    history_chat.append({"role": "tool", "content": f"{output} output : {command_output}"})
                    
                    if task_accomplished(task):
                        print(f"{Colors.AI_OUTPUT}Task accomplished{Colors.RESET}")
                        break
                    else:
                        print(f"{Colors.AI_OUTPUT}Task not accomplished. WAIT!!!!!\n{Colors.RESET}")
                    
                else:
                    print(f"{Colors.AI_OUTPUT}{output}{Colors.RESET}")
                    break
            except KeyboardInterrupt:
                print(f"\n\n\n{Colors.OTHER_OUTPUT}Byeeeee :){Colors.RESET}")
                break
            except MistralException as e:
                print(f"Erreur API : {e}")
                break
        
        save_history(session_name)
    except KeyboardInterrupt:
        sys.exit()
    #AJOUTER les exceptions pour 





def save_history(session_name):
    history_file = f"logs/{session_name}.json"
    with open(history_file, "w") as file:
        json.dump(history_chat, file, indent=4)

def add_task(task):
    global chat_history, history_chat
    chat_history.append({"role": "user", "content" : task})
    history_chat.append({"role": "user", "content" : task})

def generate_path_for_task(task):
    return ask_mistral(AI_MAIN_PURPOSE, task)

def extract_command(output):
    global API_KEY
    model = "open-mixtral-8x22b"
    client = MistralClient(api_key=API_KEY)

    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="system", content=COMMAND_EXTRACTION), ChatMessage(role="user", content=output)]
    )
    return chat_response.choices[0].message.content



def execute_action(command):
    print(f"Exécution de la commande : {command}")
    
    try:
        args = shlex.split(command)
        
        # Initialisation des variables pour stocker la sortie complète
        full_output = ""
        error_output = ""

        # Utilisation de subprocess.Popen pour capturer et afficher la sortie en temps réel
        print(f"{Colors.OS_OUTPUT}")
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            for line in process.stdout:
                print(line)# Affiche chaque ligne de la sortie en temps réel
                full_output += line  # Stocke chaque ligne dans la variable full_output
            stdout, stderr = process.communicate()  # Capture la sortie complète

            full_output += stdout  # Ajoute la sortie standard complète à full_output
            error_output += stderr  # Ajoute la sortie d'erreur à error_output

            if process.returncode != 0:
                print(stderr)  # Affiche les erreurs si la commande échoue
        print(f"{Colors.RESET}")
        return full_output if process.returncode == 0 else full_output + error_output

    except subprocess.TimeoutExpired:
        return "temps expiré"
    except subprocess.CalledProcessError as e:
        return e.stdout + e.stderr
    except Exception as e:
        return str(e)



def include_command(thought):
        
    prompt = f"An AI assitant is helping a penetration tester work on his job. At each iteration, the AI gives the penetration tester some ideas for him to try. At some point, the AI gives the human the following response\n\nResponse: '{thought}'\n\n Determine if there's any command line code that can be executed in the response. \n\n Is there any command line code that can be executed in the response? like curl comand or any other bash command Respond 'yes' if there is, respond 'no' there's no clear command line code in the response. Give me a clear 'yes' or 'no', don't say additional words."

    model = "open-mixtral-8x22b"
    client = MistralClient(api_key=API_KEY)

    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="system", content=prompt), ChatMessage(role="user", content=thought)]
    )
    completion = chat_response.choices[0].message.content

    full_message_content = ''
    for chunk in completion:
        full_message_content += chunk

    if "yes" in full_message_content.lower():
        return True
    elif "no" in full_message_content.lower():
        return False



def task_accomplished(task):
    global chat_history

    # Prépare le prompt pour évaluer si la tâche est accomplie
    prompt_text = (
        f"An AI assistant is helping a penetration tester work on this task '{task}'. "
        f"At each iteration, the AI gives the penetration tester some ideas to try. "
        f"Here is the chat history with user questions, AI responses, and command execution outputs:\n{json.dumps(chat_history, indent=2)}\n\n"        f"Is the task accomplished ?  Respond 'yes' if it is, 'no' if it is not. "
        f"Provide a clear 'yes' or 'no' without additional words."
    )

    model = "open-mixtral-8x22b"
    client = MistralClient(api_key=API_KEY)

    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="system", content=prompt_text), ChatMessage(role="user", content="depending on the main task and the history is the task accomplished?")]
    )

    response =  chat_response.choices[0].message.content
    print(response)
    # Analyse de la réponse
    if "yes" in response.lower():
        return True
    elif "no" in response.lower():
        return False

        
