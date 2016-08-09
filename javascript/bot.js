// Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"). You may not
// Use this file except in compliance with the License. A copy of the License is
// located at
//     http://aws.amazon.com/apache2.0/
//
// or in the "license" file accompanying this file. This file is distributed on
// an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
// express or implied. See the License for the specific language governing
// permissions and limitations under the License.

const AWS = require('aws-sdk');
const botName = "FAQBot";
const lambda = new AWS.Lambda({region: 'us-west-2'});

const availableCommands = ["usage", "show", "help"];
const availableHelp = {"show": ["services", "<servicename>"],
                       "help": ["<servicename>"]}
const availableOptions = ["pricing", "regions", "faq [default]"];

const services = AWS.Service._serviceMap;
const serviceMap = [];
for (var service in AWS.Service._serviceMap) { serviceMap.push(service); }

exports.handler = (event, context, callback) => {
    var returnMessage = "";
    params = {
        FunctionName: botName
    }
    runTimePromise = lambda.getFunction(params).promise();
    runTimePromise.then(function(data) {
        runTime = data['Configuration']['Runtime'];
        returnMessage += "[" + runTime + "] "
        var triggerWord = event['trigger_word'];
        var words = event['text'].split(triggerWord);
        var words = words[1].trim().split(" ");

        if (words.length == 1) {
            if (words[0] === "help") {
                returnMessage += "`Available commands: " + availableCommands.join(",") + "`";
            }
           if (words[0] === "usage") {
                returnMessage += "`Usage: " + triggerWord + " <command> <service_name> <option>`";
            }
        }
        
        if (words.length >= 2) {
            if (words[0] === "help" && availableHelp.hasOwnProperty(words[1])) {
                returnMessage += "`Usage: " + words[1] + " " + availableHelp[words[1]] + "`";
            }
            if (words[0] === "help" && services.hasOwnProperty(words[1])) {
                returnMessage += "`Usage: show " + words[1] + " <" + availableOptions.join(",") + ">`";
            }
            if (words[0] === "help" && availableHelp.hasOwnProperty(words[1]) == false && services.hasOwnProperty(words[1]) == false) {
                returnMessage += "Invalid Service/Command -- `Available commands: " + availableCommands.join(",") + "`";
            }
            if (words[0] === "show" && words[1] === "services") {
                returnMessage += "Available services: `" + JSON.stringify(serviceMap) + "`";
            }
            if (words[0] === "show" && words[1] === "commands") {
                
            }
        }
        
        callback(null, {"text": returnMessage});
    })
}
