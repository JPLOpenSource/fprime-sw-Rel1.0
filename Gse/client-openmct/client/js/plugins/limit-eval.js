function ChanLimitEval() {
    function hasNull(o) {
        for (key in o) {
            if (o[key] == null) {
                return true;
            }
        }
        return false;
    }

    function LimitEvaluator(domainObject) {
        return {
            evaluate: function(datum, key) {
                // console.log(key);
                // Return based on domainObject
                let limits = domainObject.model.limits;
                let raw = datum.value;
                if (raw > limits['high_red']) {
                    return {
                        cssClass: 's-limit-red s-limit-upr'
                    }
                } else if (raw > limits['high_orange']) {
                    return {
                        cssClass: 'limit-orange'
                    }
                } else if (raw > limits['high_yellow']) {
                    return {
                        cssClass: 's-limit-yellow s-limit-upr'
                    }
                } else if (raw < limits['low_red']) {
                    return {
                        cssClass: 's-limit-red s-limit-lwr'
                    }
                } else if (raw < limits['low_orange']) {
                    return {
                        cssClass: 'limit-orange'
                    }
                } else if (raw < limits['low_yellow']) {
                    return {
                        cssClass: 's-limit-yellow s-limit-lwr'
                    }
                } 
            }
        }
    }

    LimitEvaluator.appliesTo = function(domainObject) {
        // Applies to ref telemetry iff there are no null values in the limits
        return domainObject.type === 'ref.telemetry' && domainObject.name !== 'Events' && !hasNull(domainObject.limits);
    }

    return function install(openmct) {
        openmct.legacyExtension('capabilities', {
            key: 'limit',
            implementation: LimitEvaluator
        });
    }
}

function EventLimitEval() {

    function LimitEvaluator(domainObject) {
        return {
            evaluate: function(datum, key) {                
                // Return based on domainObject
                
                let severity = datum.severity;
           
                // Severity color coding
                if (severity === 'WARNING_HI') { 
                    return {
                        cssClass: 's-limit-red'
                    };
                } else if (severity === 'WARNING_LO') {
                    return {
                        cssClass: 's-limit-yellow'
                    };

                } else if (severity === 'COMMAND') {
                    return {
                        cssClass: 'limit-blue'
                    };

                }
            }
        }
    }

    LimitEvaluator.appliesTo = function(domainObject) {
        // Applies to ref telemetry iff there are no null values in the limits
        return domainObject.type === 'ref.telemetry' && domainObject.name === 'Events';
    }

    return function install(openmct) {
        openmct.legacyExtension('capabilities', {
            key: 'limit',
            implementation: LimitEvaluator
        });
    }
}