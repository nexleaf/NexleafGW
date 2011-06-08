
import sys
import json
import logging

from datetime import datetime
from Logging.Logger import getLog
from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, loader, RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage



