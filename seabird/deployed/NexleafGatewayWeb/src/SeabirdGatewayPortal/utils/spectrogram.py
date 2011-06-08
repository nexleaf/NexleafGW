'''
Created on Feb 20, 2011

@author: martin
'''

import sys
import json
import wave
import struct
import logging
from io import BytesIO, StringIO

from mongoengine import *

from datetime import datetime, timedelta
from Logging.Logger import getLog

from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, loader, RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import struct
import matplotlib.cm as cm


def spectrogram(response, buf, sampleRate, dev, depl, date):
    fig = Figure(figsize=(24,8), dpi=72)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.specgram(buf, NFFT=1024, Fs=sampleRate, cmap=cm.Greys, noverlap=512)
    ax.set_ylabel("Hz")
    ax.set_xlabel("Seconds")
    ax.set_title("%s %s %s" % (depl, dev, date))
    fig.subplots_adjust(left=0.04, bottom=0.07, right=0.98, \
                        top=0.95, wspace=0.20, hspace=0.00)
    canvas.print_png(response)
    

