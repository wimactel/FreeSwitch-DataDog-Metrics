#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("../eventsocket")

import eventsocket
from twisted.python import log
from twisted.internet import defer, reactor, protocol

from config import config

class FreeSwitchESLProtocol(eventsocket.EventProtocol):
    def __init__(self):
        eventsocket.EventProtocol.__init__(self)

    @defer.inlineCallbacks
    def authRequest(self, ev):
        # Try to authenticate in the eventsocket (Inbound)
        # Please refer to http://wiki.freeswitch.org/wiki/Mod_event_socket#auth
        # for more information.
        try:
            yield self.auth(config.freeSwitch.password)
        except eventsocket.AuthError, e:
            self.factory.continueTrying = False
            self.factory.ready.errback(e)

        #check for G729
        g729_available = yield self.api('g729_available') 
        

	log.msg("G729: " + g729_available.data.rawresponse)

	self.g729 = "true" in g729_available
        
        self.factory.ready.callback(self)

    @defer.inlineCallbacks
    def g729_metrics(self):
        if (self.g729):
            g729_count = yield self.api('g729_count')
            g729_count = int(g729_count)
            statsd.gauge('freeswitch.g729.total', g729_count)
            g729_counts = yield self.api('g729_used')
            g729_enc, g729_dec = [int(e) for e in g729_counts.split(":")]
            statsd.gauge('freeswitch.g729.used.encoder', g729_enc)
            statsd.gauge('freeswitch.g729.used.decoder', g729_dec)
            if (g729_enc > g729_dec):
                statsd.gauge('freeswitch.g729.utilization', g729_enc / g729_count)
            else:
                statsd.gauge('freeswitch.g729.utilization', g729_dec / g729_count)

    
    def tdmMetrics(self):
        data = yield self.api('status')
        print data.rawresponse
        
        
        
"""

+OK
span: 1 (wp1)
type: Sangoma (ISDN)
physical_status: ok
signaling_status: UP
chan_count: 24
dialplan: XML
context: belltdm
dial_regex: 
fail_dial_regex: 
hold_music: 
analog_options: none




span_id: 1
chan_id: 1
physical_span_id: 1
physical_chan_id: 1
physical_status: ok
physical_status_red: 0
physical_status_yellow: 0
physical_status_rai: 0
physical_status_blue: 0
physical_status_ais: 0
physical_status_general: 0
signaling_status: UP
type: B
state: DOWN                 THIS IS WAHT YOU CARE ABOUT
last_state: HANGUP_COMPLETE
txgain: 0.00
rxgain: 0.00
cid_date: 
cid_name: 
cid_num: 
ani: 
aniII: 
dnis: 
rdnis: 
cause: NONE
session: (none)




"""

        

class FreeSwitchESLFactory(protocol.ReconnectingClientFactory):
    maxDelay = 15
    protocol = FreeSwitchESLProtocol

    def __init__(self):
        self.ready = defer.Deferred()

@defer.inlineCallbacks
def main():

    factory = FreeSwitchESLFactory()
    reactor.connectTCP(config.freeSwitch.host, config.freeSwitch.port, factory)

    # Wait for the connection to be established
    try:
        client = yield factory.ready
    except Exception, e:
        log.err("cannot connect: %s" % e)
        defer.returnValue(None)


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    main()
    reactor.run()
