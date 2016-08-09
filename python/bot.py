# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License is
# located at
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import print_function

import re
import json
import logging
import pyutu
from pyutu import PricingContext, check_service, get_prices

print('Loading pyfaqbot function')

log = logging.getLogger()
log.setLevel(logging.DEBUG)
pyutu.client.set_log_level(None)


def _options_to_dict(options):
    opts = dict()
    for option in options:
        found = re.findall(r'(\w+)=(.+?)(?= \w+=|$)', option)
        opts.update(dict(found))
        log.info("[options_to_dict] opts: {0}".format(opts))
    return opts


def pricing(service, options=dict(), max=5):
    log.info("[pricing] service: {0} options: {1}".format(
        service, options))
    try:
        check_service(service)
        pc = None
        if 'region' in options:
            pc = PricingContext(region=options['region'])
            options.pop('region')
        else:
            pc = PricingContext(region='us-east-1')

        pc.service = service
        pc.add_attributes(options)
        prices = get_prices(pc)

        response = ''
        i = 0
        for p in prices:
            response += "Rate Code: {0} price:\n```\n{1}\n```\n".format(
                p, json.dumps(prices[p], indent=2, sort_keys=True))
            if i >= max:
                response += "*-= Hit MAX responses =-*"
                break
            i += 1

        return response
    except ValueError as ve:
        return "Price for service '{0}' not yet supported.".format(service)


def show(service, options=dict()):
    log.debug("[show] service: {0} options: {1}".format(
        service, options))

    if service is None or service == 'pricing':
        if 'region' in options:
            pc = PricingContext(region=options['region'])
            options.pop('region')
        else:
            pc = PricingContext(region='us-east-1')

        pc.add_attributes(options)
        olist = ''
        for i, o in enumerate(pc.idx['offers']):
            if i < len(pc.idx['offers']) - 1:
                olist += o + ", "
            else:
                olist += o
        return olist


def bot_help(service, options=dict()):
    log.debug("[bot_help] service_name: {0} options: {1}".format(
        service, options))
    h = "Available commands `{0}`\n".format(commands.keys())
    h += "Usage: `awsfaq <command> <service> <option1> <option2> ...`"
    return h


commands = {
    'price': pricing,
    'show': show,
    'help': bot_help
}


def lambda_handler(event, context):
    assert context
    log.debug(event)
    bot_event = event

    trigger_word = bot_event['trigger_word']
    raw_text = bot_event['text']
    raw_args = raw_text.replace(trigger_word, '').strip()

    args = raw_args.split()
    log.debug("[lambda_handler] args:{0}".format(args))

    if len(args) >= 1:
        command = args[0]

    if command not in commands:
        command = 'help'

    service = None
    if len(args) >= 2:
        service = args[1]

    options = ''
    if len(args) >= 3:
        options = args[2:]

    log.debug("[lambda_handler] command:'{0}' service:'{1}' options:'{2}'".format(
        command, service, options))
    resp = commands[command](service, _options_to_dict(options))

    return {
        'text': "{0}".format(resp)
    }
