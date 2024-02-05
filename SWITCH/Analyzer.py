#determine if the systems needs adaption. Checks if the parameters/ thresholds
#are been crosed ...........
from Planner_ada import Planner
import pandas as pd
import time
import numpy as np
import os
# from Custom_Logger import logger


    
class Analyzer():
    def __init__(self):
        
        self.time = -1
        self.count = 0


    def perform_analysis(self,monitor_dict):
        model = monitor_dict["model"] 
        image_process_time = monitor_dict["image_processing_time"] 
        confidence = monitor_dict["confidence"] 
        utility = monitor_dict["utility"]

        # change the system objective?
        # remove MAPE?
        # change set_dimmer to increase_dimmer and decrease_dimmer?


        # multiple objectives of the system
        objective='''Here the system objective is to keep the image processing time below 5 and the confidence as high as possible.'''
        


        instruction=f'You are an adaptation manager for a system handling image processing requests. This system utilizes machine learning models for object detection to process images. Self-adaptive systems are capable of modifying their runtime behavior in order to achieve system objectives. {objective} You being the adapatation manager are responsible for modifying the runtime behavior of the system using the MAPE (Monitor-Analyze-Plan-Execute) model. You will be provided data on the status of the system and you need to analyze to decide if adaption is required and what type of adaptation is needed. You can modify the system by selecting which image processing machine learning model is to be used at that time.'


        # maybe put some of this stuff into instruction?
        few_shot=['''These are the models that can be used. They are all YOLOv5 models of different sizes.
            Models -
                YOLOv5n - Speed: 6.3, Performance: 45.7
                YOLOv5s - Speed: 6.4, Performance: 56.8
                YOLOv5m - Speed: 8.2, Performance: 64.1
                YOLOv5l - Speed: 10.1, Performance: 67.3
                YOLOv5x - Speed: 12.1, Performance: 68.9
                  
        Terminology:
        Speed - the speed of the model. Higher this value, slower the model
        Performance - how well the model performs at the ML image processing task. Higher this value, better the model
        model - name of the model in use currently 
        image_processing_time - Amount of time from when an image hits the system for detection to the time when the object detection model finishes processing the image and gives output. This time includes model processing time and the time the image had to wait in the queue before before being processed.
        confidence - the confidence with which objects are detected in the image. Indicates how well the model is performing at the task.
                  

                            
        Here are a few examples on how you are to interact with the system. Respond with the action number.


        Status:
        image_processing_time:
        confidence: 

        Actions you can take:
        1. YOLOv5n
        2. YOLOv5s
        3. YOLOv5m
        4. YOLOv5l
        5. YOLOv5x
        6. Do nothing

        Answer:''', 
        '''2''',

        '''Status:
        image_processing_time:
        confidence:

        Actions you can take:
        1. YOLOv5n
        2. YOLOv5s
        3. YOLOv5m
        4. YOLOv5l
        5. YOLOv5x
        6. Do nothing

        Answer:''', 
        '''1 0.5''',

        '''Status:
        image_processing_time:
        confidence:

        Actions you can take:
        1. YOLOv5n
        2. YOLOv5s
        3. YOLOv5m
        4. YOLOv5l
        5. YOLOv5x
        6. Do nothing

        Answer:''', 
        '''1 0.2''',

        '''Status:
        image_processing_time:
        confidence:

        Actions you can take:
        1. YOLOv5n
        2. YOLOv5s
        3. YOLOv5m
        4. YOLOv5l
        5. YOLOv5x
        6. Do nothing

        Answer:''', 
        '''4''']

        closing='''Actions you can take:
        1. YOLOv5n
        2. YOLOv5s
        3. YOLOv5m
        4. YOLOv5l
        5. YOLOv5x
        6. Do nothing

        Answer:'''

        planner_obj = Planner(monitor_dict)
        planner_obj.generate_adaptation_plan(closing, instruction, few_shot)
