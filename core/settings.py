from .settings_common import *

'''
Default fallback shortcode for an aggregator that does not return a parameter in their response string to the channel.
NOTE: Be careful if you have multiple aggregators who do not return the shortcode value in thier response string.
If you have several, you may be forced to spin up multiple instances of this software as each instance can only support 
one of such aggregators if the format of requests from the channel that they expect differ.

This kind of aggregator can though provide multiple shortcodes and we can create handlers for all of them using the 
default shortcode set here. 

For example if in their API DOcs, aggregator A indicates that there response string has 
(timestamp, response_text, msisdn, transaction_id), clearly this lacks a short/service code(258*7), 
While creating handlers for all shortcodes provided by aggregator A, we should leave the shortcode field on 
the handler creation form to use the set settings.DEFAULT_SHORT_CODE value.

In case you have another different aggregator B with a similar setup as above (does not return service/short code)
these two can never exist on the same instance of the USSD external channel unless they expect the same format of 
requests from this USSD channel.
'''
DEFAULT_SHORT_CODE = "258*7"

