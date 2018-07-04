var BinaryDecoderPlugin = function (options) {

    var typeConfig = {
        name: "Binary Decoder",
        description: `Takes in binary data, translates it BSON, and
                      sends it by web socket to the provided port`,
        createable: true,
        cssClass: 'bb', //Add css class for icon here
        initialize: function () {
            //perform any necessary setup here
        }
    }

    function BinaryDecoderViewProvider () {

    }

    return function install(openmct) {
        openmct.types.addType('binary-decoder', typeConfig);
        openmct.objectViews.addProvider({
          key: 'binary-decoder',
          // Console name
          name: 'Binary Decoder',
          // What provider you want to add...
          canView: function (d) {
            return d.type === 'binary-decoder';
          },
          // Instances and destroys the command view widget.
          view: function (domainObject) {

            return {
              // Make it appear
              show: function (container) {
                //container.className += " abs";  // Open MCT bug requires this line
                //commandView.$mount(container);
                container.innerHTML('<p> Hello Binary Packets </p>')
              },
              // Destroys it
              destroy: function (container) {
                //commandView.$destroy();
              }
            }
          }
        });

        //openmct.objectViews.addProvider()
        openmct.objects.addRoot({
          key: 'binary-decoder',
          namespace: 'test.binary-decoder'
        });

        openmct.objects.addProvider('test.binary-decoder', {
          // Returning a promise containing name, id, type info.
          get: function () {
            return Promise.resolve({
              name: 'Binary Decoder',
              identifier: {
                key: 'binary-decoder',
                namespace: 'test.binary-decoder'
              },
              type: 'binary-decoder'
            });
          }
        });
    }
}
