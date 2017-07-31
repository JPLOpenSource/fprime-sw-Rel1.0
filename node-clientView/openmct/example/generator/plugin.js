/*****************************************************************************
 * Open MCT, Copyright (c) 2014-2017, United States Government
 * as represented by the Administrator of the National Aeronautics and Space
 * Administration. All rights reserved.
 *
 * Open MCT is licensed under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://www.apache.org/licenses/LICENSE-2.0.
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 * Open MCT includes source code licensed under additional open source
 * licenses. See the Open Source Licenses file (LICENSES.md) included with
 * this source code distribution or the Licensing information page available
 * at runtime from the About dialog for additional information.
 *****************************************************************************/
/*global define*/

define([
    "./GeneratorProvider",
    "./SinewaveLimitCapability"
], function (
    GeneratorProvider,
    SinewaveLimitCapability
) {

    var legacyExtensions = {
        "capabilities": [
            {
                "key": "limit",
                "implementation": SinewaveLimitCapability
            }
        ]
    };

    return function(openmct){
        //Register legacy extensions for things not yet supported by the new API
        Object.keys(legacyExtensions).forEach(function (type){
            var extensionsOfType = legacyExtensions[type];
            extensionsOfType.forEach(function (extension) {
                openmct.legacyExtension(type, extension)
            })
        });
        openmct.types.addType("generator", {
            name: "Sine Wave Generator",
            description: "For development use. Generates example streaming telemetry data using a simple sine wave algorithm.",
            cssClass: "icon-telemetry",
            creatable: true,
            form: [
                {
                    name: "Period",
                    control: "textfield",
                    cssClass: "l-input-sm l-numeric",
                    key: "period",
                    required: true,
                    property: [
                        "telemetry",
                        "period"
                    ],
                    pattern: "^\\d*(\\.\\d*)?$"
                },
                {
                    name: "Amplitude",
                    control: "textfield",
                    cssClass: "l-input-sm l-numeric",
                    key: "amplitude",
                    required: true,
                    property: [
                        "telemetry",
                        "amplitude"
                    ],
                    pattern: "^\\d*(\\.\\d*)?$"
                },
                {
                    name: "Offset",
                    control: "textfield",
                    cssClass: "l-input-sm l-numeric",
                    key: "offset",
                    required: true,
                    property: [
                        "telemetry",
                        "offset"
                    ],
                    pattern: "^\\d*(\\.\\d*)?$"
                },
                {
                    name: "Data Rate (hz)",
                    control: "textfield",
                    cssClass: "l-input-sm l-numeric",
                    key: "dataRateInHz",
                    required: true,
                    property: [
                        "telemetry",
                        "dataRateInHz"
                    ],
                    pattern: "^\\d*(\\.\\d*)?$"
                }
            ],
            initialize: function (object) {
                object.telemetry = {
                    period: 10,
                    amplitude: 1,
                    offset: 0,
                    dataRateInHz: 1,
                    values: [
                        {
                            key: "utc",
                            name: "Time",
                            format: "utc",
                            hints: {
                                domain: 1
                            }
                        },
                        {
                            key: "yesterday",
                            name: "Yesterday",
                            format: "utc",
                            hints: {
                                domain: 2
                            }
                        },
                        {
                            key: "sin",
                            name: "Sine",
                            hints: {
                                range: 1
                            }
                        },
                        {
                            key: "cos",
                            name: "Cosine",
                            hints: {
                                range: 2
                            }
                        }
                    ]
                };
            }
        });
        openmct.telemetry.addProvider(new GeneratorProvider());
    };

});
