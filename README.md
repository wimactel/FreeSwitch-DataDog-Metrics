FreeSwitch-DataDog-Metrics
==========================

A FreeSwitch ESL application that exports statistics to DataDog using the dogstatsd api. 

Intended to run on a machine that has both the datadog-agent and freeswitch running

TODO
----

* Separate hangup causes into normal/abnormal
* Better metric names
* Metrics on TDM trunks
* Rename Classes
* G729 Licensing
* Generate Alarms
* Daemonize 
* Package
* Add a config file
* Alarm on SIP gateways
* don't assume the location of eventsocket

Requirements 
------------

* [Twisted](http://twistedmatrix.com/)
* [eventsocket](https://github.com/fiorix/eventsocket)
* [dogstatsd-python](https://github.com/DataDog/dogstatsd-python)