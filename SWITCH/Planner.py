from Execute import Executor
import pandas as pd
from openai import OpenAI
# from Custom_Logger import logger
from dotenv import load_dotenv
import csv

load_dotenv()




# handles history and keeping track of the chat, handles context overflow
class Chat():
    def __init__(self,maxContext,client):
        self.chat=[]
        self.maxContext=maxContext
        self.client=client
    
    def condenseHistory(self):
        self.chat.append({"role":"user","content":'Summarize the conversation till now'})
        res=self.client.create(
            model='gpt-4',
            messages=self.chat #add max tokens?
        )
        self.chat=[{"role":"user","content":res.choices[0].message.content}]
    
    def updateChat(self,role,content,tokenCount=0):
        self.chat.append({"role":role,"content":content})
        
        if tokenCount > self.maxContext:
            des=input('Max context limit reached, wanna condense? y/n')
            if des=='y':
                self.condenseHistory()

        print(f'{role}--->{content}',flush=True)



class LLMInterface():


    def __init__(self,instruction,few_shot,closing):
        # connect to the LLM api service
        client=OpenAI().chat.completions
        print('Connected to the LLM api service',flush=True)

        self.chat=Chat(7500,client)

        self.client=client
        self.closing=closing

        # send the instruction and few shot to the LLM
        self.chat.updateChat("system",instruction)

       
        for idx,l in enumerate(few_shot):
            if idx%2==0:
                self.chat.updateChat("user",l)
            else:
                self.chat.updateChat("assistant",l)


        res=client.create(
            model='gpt-4',
            messages=self.chat.chat
        )

        self.chat.updateChat('assistant',res.choices[0].message.content)

    
    # here new needs to be a list of strings
    def set_few_shot(self,new):
        self.few_shot=new
    
    def set_instruction(self,new):
        self.instruction=new
    
    
    def construct_prompt(self,status):
        status_string="Status:\n"
        for var_name,stat in status.items():
            status_string+=f'{var_name}: {stat}\n'
        status_string+=self.closing
        return f'{status_string}'
    

    def parse_response(self,res):
        return res

        # res=res.split(" ")
        # cmdNo=int(res[0])
        # if len(res)>1:
        #     args=res[1]
        # else:
        #     args=None
        # return (cmdNo,args)


    # status is a dictionary of {variable_name:value}
    def ask(self,status):
        prompt=self.construct_prompt(status)
        self.chat.updateChat("user",prompt)
        res=self.client.create(
            model='gpt-4',
            messages=self.chat.chat #add max tokens?
        )
        self.chat.updateChat('assistant',res.choices[0].message.content,res.usage.total_tokens)
        print(f'TOKENS USED: {res.usage.total_tokens}',flush=True)
        return self.parse_response(res.choices[0].message.content)
        



class Planner():
    def __init__(self,  monitor_dict ):
        self.model = monitor_dict["model"] 
        self.model=self.model[:4].upper()+self.model[4:]
        self.image_process_time = monitor_dict["image_processing_time"] 
        self.confidence = monitor_dict["confidence"] 
        self.utility = monitor_dict["utility"]

    def generate_adaptation_plan(self , closing, instruction, few_shot):
        
        
        llmInterface=LLMInterface(instruction,few_shot,closing)

        
        res=llmInterface.ask({'model':self.model,'image_processing_time':self.image_process_time,'confidence':self.confidence})
        action = int(res)
                
        # if( model == 'nano'):
        #     action = 1
        # elif( model == "small" ):
        #     action = 2
        # elif( model == 'medium' ):
        #     action = 3
        # elif( model == 'large' ):
        #     action = 4  
        # elif( model == 'xlarge' ):
        #     action = 5
        # else:
        #     # logger.error(    {'Component': "Planner" , "Action": "No adaptation plan generated" }  )
        #     action = 1
            
        #creates Executor object and call's to perform action.
        exe_obj = Executor()
        exe_obj.perform_action(action)