from openai import OpenAI


# handles communication "thread" with an LLM
# handles history and keeping track of the chat, handles prompt generation, handles context overflow
class Chat():

    # starts the chat off
    def __init__(self,instruction,few_shot,closing,llm):
        self.chat=[]
        self.few_shot=few_shot
        self.instruction=instruction
        self.closing=closing

        # start off the chat
        self.updateChat("system",instruction)
        for idx,l in enumerate(few_shot):
            if idx%2==0:
                self.updateChat("user",l)
            else:
                self.updateChat("assistant",l)
        
        self.prompt(llm)
        
    # constructs the prompt
    def construct_prompt(self,status):
        status_string="Status:\n"
        for var_name,stat in status.items():
            status_string+=f'{var_name}: {stat}\n'
        status_string+=self.closing
        return f'{status_string}'


    # summarizes the history and resets the convo with the summary
    def condenseHistory(self,llm):
        self.chat.append({"role":"user","content":'Summarize the conversation till now'})
        res=llm.ask(self.chat)
        self.chat=[{"role":"user","content":res.choices[0].message.content}]
    

    # adds to the chat history and checks if condensation is needed
    def updateChat(self,role,content,llm=None,tokenCount=0):
        self.chat.append({"role":role,"content":content})
        
        if llm!=None and tokenCount > llm.maxContext:
            des=input('Max context limit reached, wanna condense? y/n')
            if des=='y':
                self.condenseHistory(llm)
                role='user'
                content=self.chat[0]['content']
                tokenCount=0

        print(f'{role}--->{content}')
        print(f'TOKENS USED: {tokenCount}')

    # parses the llm response
    def parse_response(self,res):
        res=res.split(" ")
        cmdNo=int(res[0])
        if len(res)>1:
            args=res[1]
        else:
            args=None
        return (cmdNo,args)
    
    # llm related functions---------------


    # prompts the llm and adds to chat history
    # chatData can be chat history or a prompt(string)
    def prompt(self,llm,chatData=None):
        if chatData!=None:
            self.updateChat('user',chatData,llm)
        res=llm.ask(self.chat)
        self.updateChat('assistant',res.choices[0].message.content,llm,res.usage.total_tokens)
        return res.choices[0].message.content

    # status is a dictionary of {variable_name:value}
    def standard_prompt(self,status,llm):
        prpt=self.construct_prompt(status)
        res=self.prompt(llm,prpt)
        return self.parse_response(res)



# responsible for communicating with the LLM API
class LLMInterface():

    def __init__(self,maxContext=7500,model='gpt-4'):
        # connect to the LLM api service
        client=OpenAI().chat.completions
        print('Connected to the LLM api service')

        self.client=client
        self.maxContext=maxContext

        
    
    def ask(self,chatData):
        res=self.client.create(
            model='gpt-4',
            messages=chatData #add max tokens?
        )
        return res
        