import logging
from django.http import HttpResponse
from couchforms.models import XFormInstance
from couchforms.views import post as couchforms_post
from receiver.signals import successful_form_received, ReceiverResult, form_received
from django.views.decorators.http import require_POST
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
from receiver import xml
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from dimagi.utils.couch.database import get_db

def home(request):
    forms = get_db().view('couchforms/by_xmlns', group=True, group_level=1)
    forms = dict([(x['key'], x['value']) for x in forms])
    return render_to_response("receiver/home.html", {"forms": forms}, RequestContext(request))
    

def form_list(request):
    """
    Serve forms for ODK. 
    """
    # based off: https://github.com/dimagi/data-hq/blob/moz/datahq/apps/receiver/views.py
    # TODO: serve our forms here
    #forms = get_db().view('reports/forms_by_xmlns', startkey=[domain], endkey=[domain, {}], group=True)
    xml = "<forms>\n"
    forms = []
    for form in forms:
        xml += '\t<form url="%(url)s">%(name)s</form>\n' % {"url": form.url, "name": form.name}
    xml += "</forms>"
    return HttpResponse(xml, mimetype="text/xml")
    

@csrf_exempt
@require_POST
def post(request):
    def callback(doc):
        def default_actions(doc):
            """These are always done"""
            doc['#export_tag'] = ["xmlns"]
            doc['submit_ip'] = request.META['REMOTE_ADDR']
            doc['path'] = request.path
            
            # if you have OpenRosaMiddleware running the headers appear here
            if hasattr(request, 'openrosa_headers'):
                doc['openrosa_headers'] = request.openrosa_headers 
            
            # a hack allowing you to specify the submit time to use
            # instead of the actual time receiver
            # useful for migrating data
            received_on = request.META.get('HTTP_X_SUBMIT_TIME')
            date_header = request.META.get('HTTP_DATE')
            if received_on:
                doc['received_on'] = received_on
            if date_header:
                doc['date_header'] = date_header
                
            # fire signals
            # We don't trap any exceptions here. This is by design, since
            # nothing is supposed to be able to raise an exception here
            form_received.send(sender="receiver", xform=doc)
            doc.save()
        
        def success_actions_and_respond(doc):
            feedback = successful_form_received.send_robust(sender="receiver", xform=doc)
            responses = []
            errors = []
            for func, resp in feedback:
                if resp and isinstance(resp, Exception):
                    logging.error("Receiver app: problem sending post-save signal %s for xform %s" \
                                  % (func, doc._id))
                    logging.exception(resp)
                    errors.append(str(resp))
                elif resp and isinstance(resp, ReceiverResult):
                    responses.append(resp)
            if errors:
                # in the event of errors, respond with the errors, and mark the problem
                doc.problem = ", ".join(errors)
                doc.save()
                response = HttpResponse(xml.get_response(message=doc.problem), status=201)
            elif responses:
                # use the response with the highest priority if we got any
                responses.sort()
                response = HttpResponse(responses[-1].response, status=201)
            else:
                # default to something generic 
                response = HttpResponse(xml.get_response(message="Success! Received XForm id is: %s\n" % doc['_id']), 
                                        status=201)
            
            # this hack is required for ODK
            response["Location"] = get_location(request)
            return response 
            
        
        def fail_actions_and_respond(doc):
            response = HttpResponse(xml.get_response(message=doc.problem), status=201)
            response["Location"] = get_location(request)
            return response
        
        
        # get a fresh copy of the doc, in case other things modified it. 
        instance = XFormInstance.get(doc.get_id)
        default_actions(instance)
        
        if instance.doc_type == "XFormInstance":
            return success_actions_and_respond(instance)
        else: 
            return fail_actions_and_respond(instance)
        
    return couchforms_post(request, callback)

def get_location(request):
    # this is necessary, because www.commcarehq.org always uses https,
    # but is behind a proxy that won't necessarily look like https
    if hasattr(settings, "OVERRIDE_LOCATION"):
        return settings.OVERRIDE_LOCATION
    prefix = "https" if request.is_secure() else "http"
    return "%s://%s" % (prefix, Site.objects.get_current().domain)
