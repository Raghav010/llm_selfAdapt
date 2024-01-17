from socket import socket, AF_INET, SOCK_STREAM
import time
from time import sleep


# the swim interface, gets and sets data on SWIM
# interacts with SWIM

# responds with 3 types of responses:
# - "Ok" - the request went through
# - the data that was requested
# - "Error" - the request didnt go through due to the SWIM being offline or some other error
# - "Strike {number} function_name" - the adaptation client tried to do something that wasnt possible by simulation, like adding a server when the max servers were already present
class SwimInterface:
    def __init__(self,HOST,PORT):
        self.socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket.connect((HOST, PORT))
        except:
            print("Error connecting to SWIM")
            self.socket=None
        self.strike_count=0
    
    def send_command(self, command):
        # command format - f'command\n'
        try:
            self.socket.sendall(command.encode() + b"\n") # sim ended
        except:
            return "Error"
        data = self.socket.recv(1024)
        data=data.decode()
        try:
            data=float(data)
            return data
        except:
            try:
                data=int(data)
                return data
            except:
                return data

    def get_dimmer(self):
        return self.send_command("get_dimmer")

    def get_servers(self):
        return self.send_command("get_servers")

    def get_active_servers(self):
        return self.send_command("get_active_servers")

    def get_max_servers(self):
        return self.send_command("get_max_servers")

    def get_utilization(self, server_id):
        command = f"get_utilization server{server_id}"
        return self.send_command(command)

    def get_basic_response_time(self):
        return self.send_command("get_basic_rt")

    def get_optional_response_time(self):
        return self.send_command("get_opt_rt")

    def get_basic_throughput(self):
        return self.send_command("get_basic_throughput")

    def get_optional_throughput(self):
        return self.send_command("get_opt_throughput")

    def get_arrival_rate(self):
        return self.send_command("get_arrival_rate")

    def add_server(self):
        cur_server_count=self.get_servers()
        if cur_server_count<self.get_max_servers():
            return self.send_command("add_server")
        else:
            self.strike_count+=1
            return f'Strike {self.strike_count} - add_server'

    def remove_server(self):
        cur_server_count=self.get_servers()
        if cur_server_count>1:
            return self.send_command("remove_server")
        else:
            self.strike_count+=1
            return f'Strike {self.strike_count} - remove_server'
     
    def set_dimmer(self, dimmer):
        if dimmer<0 or dimmer>1:
            self.strike_count+=1
            return f'Strike {self.strike_count} - set_dimmer'
        command = f"set_dimmer {dimmer}"
        return self.send_command(command)

    def get_total_utilization(self):
        utilization = 0
        active_servers = self.get_active_servers()
        for s in range(1, active_servers + 1):
            utilization += self.get_utilization(s)
        return utilization

    def get_average_response_time(self):
        basic_tput = self.get_basic_throughput()
        opt_tput = self.get_optional_throughput()

        avg_response_time = (
            basic_tput * self.get_basic_response_time()
            + opt_tput * self.get_optional_response_time()
        ) / (basic_tput + opt_tput)

        return avg_response_time

    def choose_command(self, commandNo,args=None):
        if commandNo==0:
            return self.get_dimmer()
        elif commandNo==1:
            return self.get_servers()
        elif commandNo==2:
            return self.get_active_servers()
        elif commandNo==3:
            return self.get_max_servers()
        elif commandNo==4:
            return self.get_utilization(int(args))
        elif commandNo==5:
            return self.get_basic_response_time()
        elif commandNo==6:
            return self.get_optional_response_time()
        elif commandNo==7:
            return self.get_basic_throughput()
        elif commandNo==8:
            return self.get_optional_throughput()
        elif commandNo==9:
            return self.get_arrival_rate()
        elif commandNo==10:
            self.add_server()
        elif commandNo==11:
            self.remove_server()
        elif commandNo==12:
            self.set_dimmer(float(args))
        elif commandNo==13:
            return self.get_total_utilization()
        elif commandNo==14:
            return self.get_average_response_time()
        elif commandNo==15:
            return {'dimmer':self.get_dimmer(),'active_servers':self.get_active_servers(),'max_servers':self.get_max_servers(),'utilization':self.get_total_utilization(),'avg_response_time':self.get_average_response_time(),'arrival_rate':self.get_arrival_rate()}

    def __del__(self):
        if self.socket:
            self.socket.close()


# print("You can use the following commands:")
# print("0. get_dimmer")
# print("1. get_servers")
# print("2. get_active_servers")
# print("3. get_max_servers")
# print("4. get_utilization <server_id>")
# print("5. get_basic_response_time")
# print("6. get_optional_response_time")
# print("7. get_basic_throughput")
# print("8. get_optional_throughput")
# print("9. get_arrival_rate")
# print("10. add_server")
# print("11. remove_server")
# print("12. set_dimmer <dimmer>")
# print("13. get_total_utilization")
# print("14. get_average_response_time")
# print("15. get all")
# print("Enter command number followed by arguments separated by space")
# print(f"Type q to exit\n\n\n")

# cmd=None
# while cmd!="q":
#     cmd=input("Enter command: ")
#     cmd=cmd.split(" ")
#     cmdNo=int(cmd[0])
#     if len(cmd)>1:
#         args=cmd[1]
#     else:
#         args=None
#     print(swimClient.choose_command(cmdNo,args))


class LLMInterface():
    def __init__(self,api_key,instruction,few_shot,closing):
        # connect to the LLM api service
        self.instruction=instruction
        self.few_shot=few_shot
        self.closing=closing
        
    def set_few_shot(self,new):
        self.few_shot=new
    
    def set_instruction(self,new):
        self.instruction=new
    
    # include instruction and few shot in every prompt??
    def construct_prompt(self,status):
        status_string="Status:\n"
        for var_name,stat in status.items():
            status_string+=f'{var_name}: {stat}\n'
        status_string+=self.closing
        return f'{self.instruction}\n\n{self.few_shot}\n\n{status_string}'
    
    def parse_response(self,res):
        res=res.split(" ")
        cmdNo=int(res[0])
        if len(res)>1:
            args=res[1]
        else:
            args=None
        return (cmdNo,args)
        # parse the response and return a number/action to take
        # return sim_over if the simulation is over

    # status is a dictionary of {variable_name:value}
    def ask(self,status):
        prompt=self.construct_prompt(status)
        # send to api
        # parse and return response
        



api_key=None

# change the system objective?
# remove MAPE?
# change set_dimmer to increase_dimmer and decrease_dimmer?


instruction='''You are an adpatation manager for a server system handling user requests. Self-adaptive systems are capable of modifying their runtime behavior in order to achieve system objectives. Here the system objective is to keep the average response time as low as possible. You being the adapatation manager are responsible for modifying the runtime behavior of the system using the MAPE (Monitor-Analyze-Plan-Execute) model. You will be provided data on the status of the system and you need to analyze to decide if adaption is required and what type of adaptation is needed. The possible actions you can take to modify the system are adding a server, removing a server and changing the dimmer value.
Terminology: 
dimmer - used to control the proportion of responses that include the optional content, with 1 being the setting in which all responses include the optional content, 0 when no one does (i.e., blackout). The value of the dimmer can be thought of as the probability of a response including the optional content, thus taking values in [0..1].
active_servers - the number of servers that are currently active and processing requests
max_servers - the maximum number of servers that can be active at any time
utilization - the proportion of time that all servers are busy processing requests
average_response_time - the average time taken to process a request
arrival_rate - the average number of requests arriving per second
'''

few_shot='''Here are a few examples on how you are to interact with the system. Respond with the action number. If the action has a parameter like set dimmer respond with action number followed by the dimmer value.


Status:
dimmer: 0.9
active_servers: 2
max_servers: 3
utilization: 0.0611121
average_response_time: 0.07638993128912003
arrival_rate: 11.3332

Actions you can take:
1. Set dimmer
2. Add server
3. Remove server
4. Do nothing

Answer: 
2

Status:
dimmer: 0.9
active servers: 3
max servers: 3
utilization: 0.779628
average response time: 0.07346221086027917
arrival rate: 10.6167

Actions you can take:
1. Set dimmer
2. Add server
3. Remove server
4. Do nothing

Answer: 
1 0.5

Status:
dimmer: 0.5
active servers: 3
max servers: 3
utilization: 0.517234
average response time: 0.05673555607704635
arrival rate: 9.1

Actions you can take:
1. Set dimmer
2. Add server
3. Remove server
4. Do nothing

Answer: 
1 0.2

Status:
dimmer: 0.2
active servers: 3
max servers: 3
utilization: 0.39712899999999995
average response time: 0.040725613054705435
arrival rate: 9.76667

Actions you can take:
1. Set dimmer
2. Add server
3. Remove server
4. Do nothing

Answer: 
4
'''

closing='''Actions you can take:
1. Set dimmer
2. Add server
3. Remove server
4. Do nothing

Answer:'''




swimClient=SwimInterface("127.0.0.1",4242)
if swimClient.socket==None:
    exit(0)
llmInterface=LLMInterface("api_key",instruction,few_shot,closing)


alive=swimClient.get_dimmer()
start=time.time()
while alive!='Error':
    status=swimClient.choose_command(15)
    status['time']=time.time()-start
    res=llmInterface.ask(status)
    swimClient.choose_command(res[0],res[1])
    alive=swimClient.get_dimmer() # checking if simulation is still running
    sleep(200)







