FreeSwitch-DataDog-Metrics
==========================

A FreeSwitch ESL application that exports statistics to DataDog using the dogstatsd api. 

Intended to run on a machine that has both the datadog-agent and freeswitch running.

Will automatically capture G729 licensing metrics, if mod\_com\_g729 is enabled. 

TODO
----

* Separate hangup causes into normal/abnormal
* Better metric names
* Metrics on TDM trunks
* Rename Classes
* Generate Alerts
* Daemonize 
* Package
* Add a config file
* Alert on SIP gateways
* don't assume the location of eventsocket
* add the following metrics
	* Many [Sofia Events](http://wiki.freeswitch.org/wiki/Mod_sofia#Custom_Events) (Registry?)


Alerts
------

* SHUTDOWN
* MODULE\_LOAD
* RELAODXML
* Many [Sofia Events](http://wiki.freeswitch.org/wiki/Mod_sofia#Custom_Events)

Sofia
-----

`event plain CUSTOM sofia::register sofia::expire`


Configuration
-------------

* DataDog API Key
* EventSocket Password (defaults to ClueCon)
* EventSocket Host (defaults to localhost)
* EventSocket Port (Defaults to 8021)
* DogStatsD Port (defaults to ?)
* Normal hangup causes

Requirements 
------------

* [Twisted](http://twistedmatrix.com/)
* [eventsocket](https://github.com/fiorix/eventsocket)
* [dogstatsd-python](https://github.com/DataDog/dogstatsd-python)
* YAML

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