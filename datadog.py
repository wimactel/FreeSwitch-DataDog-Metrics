#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("../eventsocket")

import eventsocket
from twisted.python import log
from twisted.internet import defer, reactor, protocol

from statsd import statsd

class MyProtocol(eventsocket.EventProtocol):
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

        # Set the events we want to get.
        yield self.eventplain("CHANNEL_CREATE CHANNEL_HANGUP CHANNEL_HANGUP_COMPLETE")

        # Tell the factory that we're ready. Pass the protocol
        # instance as argument.
        self.factory.ready.callback(self)

    def onChannelCreate(self, ev):
        log.msg('New Channel!')
        statsd.increment('freeswitch.channels.started',1)
        statsd.increment('freeswitch.channels',1)
        
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
        log.msg('Channel Complete Hangup!')
    
    @defer.inlineCallbacks 
    def fetch729(self):
        result = yield self.api('g729_used')
        log.msg(result)

class MyFactory(protocol.ReconnectingClientFactory):
    maxDelay = 15
    protocol = MyProtocol

    def __init__(self, password):
        self.ready = defer.Deferred()
        self.password = password

@defer.inlineCallbacks
def main():
    factory = MyFactory(password="ClueCon")
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