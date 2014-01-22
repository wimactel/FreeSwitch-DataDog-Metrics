#!/usr/bin/env python
# coding: utf-8

import sys

from zope.interface import implements

from twisted.internet import reactor

from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer
from twisted.python import log

from twisted.web.client import Agent
from twisted.web.http_headers import Headers

try:
    import simplejson as json
except ImportError:
    import json

from config import config

class DataDog:
    def event(self, title, text, date_happened=None, handle=None, priority=None, related_event_id=None, tags=None, host=config.dataDog.eventHostName, device_name=None, aggregation_key="FreeSwitch", source_type_name="FreeSwitch", **kwargs):
        if config.dataDog.apiKey:
            body = {
                'title': "%s: %s" % (config.dataDog.eventHostName, title),
                'text': text,
            }

            if date_happened is not None:
                body['date_happened'] = date_happened

            if handle is not None:
                body['handle'] = handle

            if priority is not None:
                body['priority'] = priority

            if related_event_id is not None:
                body['related_event_id'] = related_event_id

            if tags is not None:
                body['tags'] = ','.join(tags)

            if host is not None:
                body['host'] = host

            if device_name is not None:
                body['device_name'] = device_name

            if aggregation_key is not None:
                body['aggregation_key'] = aggregation_key
                
            if source_type_name is not None:
                body['source_type_name'] = source_type_name

            body.update(kwargs)
            
            d = Agent(reactor).request('POST', 'https://app.datadoghq.com/api/v1/events?api_key='+config.dataDog.apiKey, Headers({'Content-Type': ['application/json']}), JSONProducer(body))
            d.addCallbacks(self.eventHandleResponse, self.eventHandleError)

    def eventHandleResponse(self, r):
        pass
        
    def eventHandleError(self, reason):
        log.msg("In Error")
        reason.printTraceback()

class JSONProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = json.dumps(body)
        self.length = len(self.body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

datadog = DataDog()
    
if __name__ == "__main__":
    log.startLogging(sys.stdout)
    datadog.event("test event", "this is a test event", priority='low')
    reactor.run()
