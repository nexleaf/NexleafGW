'''
Created on Nov 1, 2010

@author: surya
'''

import os
import sys
import json
import time

from datetime import datetime
from Collections.UploadData import *
from Collections.DeploymentData import *
from Collections.DeviceData import *
from Collections.Metrics import *
from Collections.CampaignData import *
from django.core.management.base import BaseCommand, CommandError
import gridfs

class Command(BaseCommand):
    help = 'Initializes the Server: \n 1. Checks if mongod is running \n 2. Checks if mongoengine is installed'
     
    def handle(self, *args, **options):
        ''' The NexleafWebPortall initialization method.
        '''
        
        # Check if we have the right number of arguments
        #if len(args) != 1:
        #    raise CommandError('Error insufficient params: use ./manage.py init -help for info')
        
        # Check if mongod, is running
        isMongod = False
        processes = os.popen('''ps axo "%c"''')
        for process in processes:
            if 'mongod' in process:
                isMongod = True
        
        if not isMongod:
            raise CommandError('Error please run mongod first')
        
        # Import mongoengine and connect to the database
        try:
            import mongoengine
        except:
            raise CommandError('Error importing from mongoengine. Please ensure that mongoengine is installed')
        
        # Drop the database SuryaDB (This Implies That we lose all the stored images as well)
        db = mongoengine.connect('SeabirdGWDB')
        gfs = gridfs.GridFS(db)
        
        UploadData.drop_collection()
        DeviceData.drop_collection()
        DeploymentData.drop_collection()
        MetricsDeviceDaily.drop_collection()
        MetricsDeploymentDaily.drop_collection()
        CampaignData.drop_collection()
        #CampaignDeploymentInfo.drop_collection() #... embedded doc, so no drop

        for fname in gfs.list():
            f = gfs.get_last_version(fname)
            gfs.delete(f._id)
        
    
        
