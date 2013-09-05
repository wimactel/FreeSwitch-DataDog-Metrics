#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("../eventsocket")

import eventsocket
from twisted.python import log
from twisted.internet import defer, reactor, protocol

from statsd import statsd

class FreeSwitchESLProtocol(eventsocket.EventProtocol):
    def __init__(self):
        eventsocket.EventProtocol.__init__(self)

    @defer.inlineCallbacks
    def authRequest(self, ev):
        # Try to authenticate in the eventsocket (Inbound)
        # Please refer to http://wiki.freeswitch.org/wiki/Mod_event_socket#auth
        # for more information.
        try:
            yield self.auth(self.factory.password)
        except eventsocket.AuthError, e:
            self.factory.continueTrying = False
            self.factory.ready.errback(e)

		#check for G729
		self.g729 = "true" in yield self.api('g729_available')
		
        # Set the events we want to get.
        yield self.eventplain("CHANNEL_CREATE CHANNEL_HANGUP CHANNEL_HANGUP_COMPLETE")

        # Tell the factory that we're ready. Pass the protocol
        # instance as argument.
        self.factory.ready.callback(self)

    def onChannelCreate(self, ev):
        statsd.increment('freeswitch.channels.started',1)
        statsd.increment('freeswitch.channels',1)
        statsd.increment('freeswitch.call.direction.'+ ev.Call-Direction)
        if (self.g729):
        	g729_metrics()
        
    def onChannelHangup(self, ev):
        statsd.increment('freeswitch.channels.finished',1)
        statsd.decrement('freeswitch.channels',1)
        if (ev.Hangup_Cause in ["NORMAL_CLEARING"]):
            statsd.increment('freeswitch.channels.finished.normally',1)
            statsd.increment('freeswitch.channels.finished.normally.'+ev.Hangup_Cause.lower(),1)
        else:
            statsd.increment('freeswitch.channels.finished.abnormally',1)
            statsd.increment('freeswitch.channels.finished.abnormally.'+ev.Hangup_Cause.lower(),1)	

    def onChannelHangupComplete(self, ev):
    	statsd.histogram('freeswitch.rtp.skipped_packet.in', ev.variable_rtp_audio_in_skip_packet_count)
    	statsd.histogram('freeswitch.rtp.skipped_packet.out', ev.variable_rtp_audio_out_skip_packet_count)
		statsd.increment('freeswitch.caller.context.'+ev.Caller-Context)
    	statsd.increment('freeswitch.caller.source.'+ev.Caller-Source)
    
    @defer.inlineCallbacks 
    def g729_metrics(self):
    	g729_count = yield self.api('g729_count')
    	statsd.gauge('freeswitch.g729.total', g729_count)
    	g729_enc, g729_dec = (yield self.api('g729_used'))).split(":")
    	statsd.gauge('freeswitch.g729.used.encoder', g729_enc)
    	statsd.gauge('freeswitch.g729.used.decoder', g729_dec)
    	if (g729_enc > g729_dec):
    		statsd.gauge('freeswitch.g729.utilization' g729_enc / g729_count)
    	else:
    		statsd.gauge('freeswitch.g729.utilization' g729_dec / g729_count)

class FreeSwitchESLFactory(protocol.ReconnectingClientFactory):
    maxDelay = 15
    protocol = FreeSwitchESLProtocol

    def __init__(self, password):
        self.ready = defer.Deferred()
        self.password = password

@defer.inlineCallbacks
def main():
    factory = FreeSwitchESLFactory(password="ClueCon")
    reactor.connectTCP("127.0.0.1", 8021, factory)

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