FreeSwitch-DataDog-Metrics
==========================

*Currently not a functional application.*

A FreeSwitch ESL application that exports statistics to DataDog using the dogstatsd api. 

Intended to run on a machine that has both the datadog-agent and freeswitch running.

Will automatically capture G729 licensing metrics, if mod\_com\_g729 is enabled. 

TODO
----

* update metrics in readme
* update metrics table formatting in readme
* Separate hangup causes into normal/abnormal
* Better metric names
* Metrics on TDM trunks
* Generate Alerts
* [Daemonize](https://github.com/eagafonov/python-twisted-startup-script/blob/master/python-twisted-startup-script) 
* Package
* Add a config file
* Alert on SIP gateways
* don't assume the location of eventsocket
* add the following metrics
	* Many [Sofia Events](http://wiki.freeswitch.org/wiki/Mod_sofia#Custom_Events) (Registry?)


Alerts
------

* RELAODXML
* Many [Sofia Events](http://wiki.freeswitch.org/wiki/Mod_sofia#Custom_Events)
    * sofia::gateway_add INFO
    * sofia::gateway_delete INFO
    * sofia::gateway_state - when a gateway is detected as down or back up SUCCESS | ERROR

Sofia
-----

`event plain CUSTOM sofia::register sofia::expire`


Configuration
-------------

You only need a configuration file if:

* FreeSwtich has a custom ESL config
* You're monitoring a remote machine
* You'd like datadog to alarm
* You're running dogstatsd on a custom port
* You're connecting to a remote dogstatsd

If there's no API key present, no alarms will be emitted.

Any values left unpopulated have sensible defaults. 

By default, the only normal hangup cause is NORMAL_CLEARING. 

```yaml
---
DataDog:
    API_KEY: KEY
    Port: 0
    Event_Host_Name: myhostname
FreeSwitch:
    Password: ClueCon
    Host: 127.0.0.1
    Port: 8021
    Normal_Hangup_Causes: 
        - NORMAL_CLEARING
        - NORMAL_TEMPORARY_FAILURE
        - USER_BUSY
        - NO_ANSWER
        - NO_ROUTE_DESTINATION
        
```

Requirements 
------------

* [Twisted](http://twistedmatrix.com/)
* [eventsocket](https://github.com/fiorix/eventsocket)
* [dogstatsd-python](https://github.com/DataDog/dogstatsd-python)
* [PyYAML](http://pyyaml.org)

Metrics
-------

| Stat                                             | Type           | Description  |
| freeswitch.channels                              | counter 		| Number of currently active channels  |
| freeswitch.channels.started                      | counter 		| Number of channels that were started |
| freeswitch.channels.finished                     | counter 		| Number of channels that were hungup  |
| freeswitch.channels.finished.normally            | counter 		| Number of channels that were hungup normally  |
| freeswitch.channels.finished.normally.[cause]    | counter 		| Number of channels that were hungup normally for a given cause  |
| freeswitch.channels.finished.abnormally          | counter 		| Number of channels that were hungup abnormally  |
| freeswitch.channels.finished.abnormally.[cause]  | counter 		| Number of channels that were hungup abnormally for a given cause|