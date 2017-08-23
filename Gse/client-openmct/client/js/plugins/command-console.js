function CommandConsole(site, port) {

    return function install(openmct) {

        openmct.objects.addRoot({
            key: 'console',
            namespace: 'ref.command'
        });

        openmct.objects.addProvider('ref.command', {
            get: function () {
                return Promise.resolve({
                    name: 'Command Console',
                    identifier: {
                        key: 'console',
                        namespace: 'ref.command'
                    },
                    type: 'ref.command'
                });
            }
        });

        openmct.mainViews.addProvider({
            name: 'Command Console',
            canView: function (d) {
                return d.type === 'ref.command';
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

