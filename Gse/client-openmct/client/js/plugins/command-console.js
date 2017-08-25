/*
 * Install function for command widget
 */
function CommandConsole(target, site, port) {
  let targetKey = target.toLowerCase();

  return function install(openmct) {

    openmct.objects.addRoot({
      key: 'console',
      namespace: targetKey + '.command'
    });

    openmct.objects.addProvider(targetKey + '.command', {
      // Returning a promise containing name, id, type info.
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
      // Console name
      name: 'Command Console',
      // What provider you want to add...
      canView: function (d) {
        return d.type === targetKey + '.command';
      },
      // Instances and destroys the command view widget.
      view: function (domainObject) {
        var commandView = new CommandView({
          data: {
            socket: new WebSocket('ws://' + site + ':' + port.toString()),
            showCmdSearchResults: true,
            selectedHistory: ''
          }
        });

        return {
          // Make it appear
          show: function (container) {
            container.className += " abs";  // Open MCT bug requires this line
            
            commandView.$mount(container);
          },
          // Destroys it
          destroy: function (container) {
            commandView.$destroy();
          }
        }
      }
    });
  }
}

