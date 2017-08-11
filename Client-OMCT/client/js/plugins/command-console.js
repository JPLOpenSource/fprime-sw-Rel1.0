function CommandConsole() {

	// const site = 'localhost';
	// const cmdPort = 1339;

	// var socket = new WebSocket('ws://' + site + ':' + cmdPort.toString());
	// new Vue({
	var CommandView = Vue.extend({
	  template: $('#commandTemplate').text(),
	  // el:'#console',
	  data: function () {
	    return {
	      searchActive: false,
	      cmd: '',
	      cmdSearch: [],
	      cmdHist: [],
	      cmdHistQuery: '',
	      cmdHistToShow: []
	    }
	  },
	  methods: {
	    getCommands: function () {
	      // Returns promise of array of all commands
	      return getDictionary().then(function (dict) {
	        let commandDict = dict['isf']['commands'];       
	        let validCommands = [];
	        for (id in commandDict) {
	          let args = commandDict[id]['arguments'];
	          let argFormat = args.map((a) => a['name'] + ' (' + a['type'] + ') ');
	          validCommands.push({
	            'name': commandDict[id]['name'],
	            'args': argFormat
	          });
	        }
	        return validCommands;
	      });
	    },
	    sendCmd: function (event) {
	      // Add command and time
	      socket.send(this.cmd);
	      this.cmdHist.push({
	        cmd: this.cmd,
	        time: Date()
	      });
	      this.cmdHistToShow = this.cmdHist.slice();
	      this.cmdSearch = [];  // Clear search
	    },
	    searchCmd: function (event) {
	      if (this.cmd !== '') {

	        self = this;  // Avoid 'this' scoping issues inside .then of promise
	        self.getCommands().then(function (vc) {
	          self.cmdSearch = vc.filter((c) => c['name'].toLowerCase().indexOf(self.cmd.toLowerCase()) !== -1);
	        });

	      } else {
	        this.cmdSearch = [];
	      }
	    },
	    select: function (command, hist) {
	      if (hist) {
	        // If selection is from history, select entire command with arguments
	        this.cmd = command;
	      } else {
	        // Otherwise, just select command
	        this.cmd = command['name'] + '(';
	      }
	    },
	    searchHist: function () {
	      if (this.cmdHistQuery !== '') {
	        this.cmdHistToShow = this.cmdHist.filter((c) => c.cmd.toLowerCase().indexOf(this.cmdHistQuery.toLowerCase()) !== -1);
	      } else {
	        this.cmdHistToShow = this.cmdHist.slice();  // Copy command history into buffer
	      }
	    },
	  },
	  computed: {
	    reverseCmd: function () {
	      return this.cmdHistToShow.reverse()
	    }
	  }
	});

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

