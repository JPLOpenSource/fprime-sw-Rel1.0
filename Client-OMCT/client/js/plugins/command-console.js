function CommandConsole() {

    return function install(openmct) {

        openmct.objects.addRoot({
            key: 'console',
            namespace: 'isf.command'
        });

        openmct.objects.addProvider('isf.command', {
            get: function () {
                return Promise.resolve({
                    name: 'Command Console',
                    identifier: {
                        key: 'console',
                        namespace: 'isf.command'
                    },
                    type: 'isf.command'
                });
            }
        });

        openmct.mainViews.addProvider({
            name: 'Command Console',
            canView: function (d) {
                return d.type === 'isf.command';
            },
            view: function (domainObject) {
                var commandView = new CommandView();

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

