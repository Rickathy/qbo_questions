#!/usr/bin/env python
#
#Copyright (C) 2012 Thecorpora Inc.
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import roslib; roslib.load_manifest('qbo_questions')
import rospy
from qbo_listen.msg import Listened
from qbo_talk.srv import Text2Speach
from qbo_system_info.srv import AskInfo

from qbo_face_msgs.msg import FacePosAndDist

import random


global client_speak
global face_detected

def speak_this(text):
    global client_speak
    client_speak(str(text))

def listen_callback(data):
    global face_detected  
    global dialogue
    sentence = data.msg
    rospy.loginfo("Listened: |"+sentence+"|")
   
    if not face_detected:
       rospy.loginfo("Ignoring last sentece because face was not detected")
       return


    

    if sentence in dialogue:
        output = dialogue[sentence]
        print random.choice(output)
        speak_this(random.choice(output))


    elif sentence=="WHAT TIME IS IT":
        rospy.wait_for_service("/pluginsystem");
        service_pluginsystem = rospy.ServiceProxy('/pluginsystem', AskInfo)
        info = service_pluginsystem("hour")
        rospy.loginfo(info.info)
        speak_this(info.info)
    elif sentence=="WHAT DAY IS IT TODAY":
        rospy.wait_for_service("/pluginsystem");
        service_pluginsystem = rospy.ServiceProxy('/pluginsystem', AskInfo)
        info = service_pluginsystem("hdate")
        rospy.loginfo(info.info)
        speak_this(info.info)


def face_callback(data):
    global face_detected
    face_detected = data.face_detected	

def main():
    global client_speak
    global face_detected
    face_detected = False


    # We load the dialgues from the config folder
    global dialogue
    dialogue = {}
    f = open('../config/dialogues')    
    for line in f.readlines():
        try:
            line = line.replace("\n","")
            parts = line.split(">>>")

            dialogue_input = parts[0]
            dialogue_output = parts[1]
        
            # we check wheter the input line alreayd exists, if so, we add to its own list
            if dialogue_input in dialogue:
                list_of_answers = dialogue[dialogue_input]
                list_of_answers.append(dialogue_output)
                dialogue[dialogue_input] = list_of_answers
            else:
                #dialogue_input does not exist
                dialogue[dialogue_input] = [dialogue_output]
        except:
            pass        

    f.close()    

    rospy.init_node('questions')
    rospy.loginfo("Starting questions node")
    client_speak = rospy.ServiceProxy("/qbo_talk/festival_say", Text2Speach)
    subscribe=rospy.Subscriber("/listen/en_default", Listened, listen_callback)

    rospy.Subscriber("/qbo_face_tracking/face_pos_and_dist", FacePosAndDist, face_callback)


    
    rospy.spin()


if __name__ == '__main__':
    main()

