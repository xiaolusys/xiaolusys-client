'''
Created on 2012-6-1

@author: user1


'''
import winsound

print winsound.__dict__
winsound.PlaySound("SystemExit", winsound.SND_ALIAS)

winsound.PlaySound("*", winsound.SND_ALIAS)