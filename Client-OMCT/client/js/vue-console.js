function SetupConsole() {
  const site = 'localhost';
  const cmdPort = 1339;

  var socket = new WebSocket('ws://' + site + ':' + cmdPort.toString());

  function getCommands() {
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
  }

  Vue.directive('focus', {
    bind: function () {
      Vue.nextTick(function() {
        object.focus();
      });
    }
  });

  var command = new Vue({
    el: '#command',
    data: {
      searchActive: false,
      cmd: '',
      cmdSearch: [],
      cmdHist: [],
      cmdHistQuery: '',
      cmdHistToShow: []
      
    },
    methods: {
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

          self = this;  // Avoid 'this' scoping issues
          getCommands().then(function (vc) {
            self.cmdSearch = vc.filter((c) => c['name'].toLowerCase().indexOf(self.cmd.toLowerCase()) !== -1);
          });

        } else {
          this.cmdSearch = [];
        }

        // Select from search results with arrow keys
        // let i = 0;
        // if (i >= 0 && i < this.cmdSearch.length) {
        // // if(true) {
        //     case 'ArrowDown': {
        //       this.select(this.cmdSearch[i], false);
        //       i += 1;

        //       break;
        //     } 
        //     case 'ArrowUp': {
        //       this.select(this.cmdSearch[i], false);
        //       i -= 1;

        //       break;
        //     }
        //     case 'Escape': {
        //       this.cmdSearch = [];

        //       break;
        //     }

        //     default: {
        //       // Nothing todo
        //       break;
        //     }
        //   }
        // }
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
      }
    },
    computed: {
      reverseCmd: function () {
        return this.cmdHistToShow.reverse()
      }
    }
  });
}