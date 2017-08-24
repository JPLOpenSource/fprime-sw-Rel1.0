function CommandConsole(target, site, port) {
    let targetKey = target.toLowerCase();

    return function install(openmct) {

        openmct.objects.addRoot({
            key: 'console',
            namespace: targetKey + '.command'
        });

        openmct.objects.addProvider(targetKey + '.command', {
            get: function () {
                return Promise.resolve({
                    name: 'Command Console',
                    identifier: {
                        key: 'console',
                        namespace: targetKey + '.command'
                    },
                    type: targetKey + '.command'
                });
            }
        });

        openmct.mainViews.addProvider({
            name: 'Command Console',
            canView: function (d) {
                return d.type === targetKey + '.command';
            },
            view: function (domainObject) {
                var commandView = new CommandView({
                    data: {
                        socket: new WebSocket('ws://' + site + ':' + port.toString()),
                        showCmdSearchResults: true
                    }
                });

                return {
                    show: function (container) {
                        container.className += " abs";	// Open MCT bug requires this line
                        
                        commandView.$mount(container);
                    },
                    destroy: function (container) {
                        commandView.$destroy();
                    }
                }
            }
        });
    }
}

