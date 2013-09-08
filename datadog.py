#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("../eventsocket")

import eventsocket
from twisted.python import log
from twisted.internet import defer, reactor, protocol

from statsd import statsd

class FreeSwitchESLProtocolConfig(object):  

    def __init__(self):
        import yaml
        try:
            self.raw_config = yaml.load(file('config.yaml', 'r'))
        except:
            self.raw_config = {}
        
        self.dataDog = DataDogConfig(self.raw_config.get("DataDog", {}))
        
        self.freeSwitch = FreeSwitchConfig(self.raw_config.get("FreeSwitch", {}))

    def __repr__(self):
        return repr(self.raw_config)
            
class hostConfig(object):
    def __init__(self, values):
        self.raw_config = values
    
    def default_host(self):
        return "localhost"
    
    @property    
    def host(self):
        return self.raw_config.get("host", self.default_host())
    
    @property    
    def port(self):
        return self.raw_config.get("port", self.default_port())
        
    def __repr__(self):
        return repr(self.raw_config)    
                
class DataDogConfig(hostConfig):
    def __init__(self, values):
        hostConfig.__init__(self, values)
        
    def default_port(self):
        return 8125
    
    @property    
    def apiKey(self):
        return self.raw_config.get("API_KEY", None)

class FreeSwitchConfig(hostConfig):
    def __init__(self, values):
        hostConfig.__init__(self, values)

    def default_port(self):
        return 8021

    @property
    def password(self):
       return self.raw_config.get("API_KEY", "ClueCon")

    @property
    def normalHangupCauses(self):
        return self.raw_config.get("API_KEY", ["NORMAL_CLEARING"])

class FreeSwitchESLProtocol(eventsocket.EventProtocol):
    def __init__(self):
        eventsocket.EventProtocol.__init__(self)
        
        self.config = FreeSwitchESLProtocolConfig()

    @defer.inlineCallbacks
    def authRequest(self, ev):
        # Try to authenticate in the eventsocket (Inbound)
        # Please refer to http://wiki.freeswitch.org/wiki/Mod_event_socket#auth
        # for more information.
        try:
            yield self.auth(self.config.freeSwitch.password)
        except eventsocket.AuthError, e:
            self.factory.continueTrying = False
            self.factory.ready.errback(e)

        #check for G729
        g729_available = yield self.api('g729_available') 
        self.g729 = "true" in g729_available

        # Set the events we want to get.
        yield self.eventplain("CHANNEL_CREATE CHANNEL_HANGUP CHANNEL_HANGUP_COMPLETE HEARTBEAT")

        # Tell the factory that we're ready. Pass the protocol
        # instance as argument.
        self.factory.ready.callback(self)

    def onHeartbeat(self, ev):
        statsd.gauge('freeswitch.channels', ev.Session-Count)

    def onChannelCreate(self, ev):
        statsd.increment('freeswitch.channels.started')
        statsd.increment('freeswitch.call.direction.'+ ev.Call-Direction)
        if (self.g729):
            g729_metrics()
        
    def onChannelHangup(self, ev):
        statsd.increment('freeswitch.channels.finished')
        if (ev.Hangup_Cause in self.config.freeSwitch.normalHangupCauses):
            statsd.increment('freeswitch.channels.finished.normally')
            statsd.increment('freeswitch.channels.finished.normally.'+ev.Hangup_Cause.lower())
        else:
            statsd.increment('freeswitch.channels.finished.abnormally')
            statsd.increment('freeswitch.channels.finished.abnormally.'+ev.Hangup_Cause.lower())

    def onChannelHangupComplete(self, ev):
        statsd.histogram('freeswitch.rtp.skipped_packet.in', ev.variable_rtp_audio_in_skip_packet_count)
        statsd.histogram('freeswitch.rtp.skipped_packet.out', ev.variable_rtp_audio_out_skip_packet_count)
        statsd.increment('freeswitch.caller.context.'+ev.Caller-Context)
        statsd.increment('freeswitch.caller.source.'+ev.Caller-Source)
    
    @defer.inlineCallbacks 
    def g729_metrics(self):
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

class FreeSwitchESLFactory(protocol.ReconnectingClientFactory):
    maxDelay = 15
    protocol = FreeSwitchESLProtocol

    def __init__(self):
        self.ready = defer.Deferred()

@defer.inlineCallbacks
def main():

    factory = FreeSwitchESLFactory()
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