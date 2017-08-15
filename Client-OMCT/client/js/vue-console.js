var CommandView = Vue.extend({
  template: $('#commandTemplate').text(),
  data: function () {
    return {
      command_search: {
        searchActive: true,
        cmd: '',
        results: [],
        saveCmd: '',
        resultIndex: -1
      },
      command_hist: {
        history: [],
        query: '',
        results: []
      }
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

      this.socket.send(this.command_search.cmd);
      this.command_hist.history.push({
        cmd: this.command_search.cmd,
        time: Date()
      });
      this.command_hist.results = this.command_hist.history.slice();
      this.command_search.results = [];  // Clear search
    },
    searchCmd: function (event) {
      let keyPressed = event.key;
      if (this.command_search.searchActive) {
        if (this.command_search.cmd !== '') {
          console.log(event.key);

          self = this;  // Avoid 'this' scoping issues inside .then of promise
          self.getCommands().then(function (vc) {
            self.command_search.results = vc.filter(function (c) {
              return c['name'].toLowerCase()  // Case insensitive search
                              .indexOf(self.command_search.cmd.toLowerCase()  // Case insensitive query
                                                              .split('(')[0]) !== -1  // Check only name of query
            });
          });
          this.command_search.saveCmd = this.command_search.cmd;  // Save command after search

        } else {
          this.command_search.results = [];
          if (keyPressed == 'ArrowDown') {
            self = this;
            self.getCommands().then(function (vc) {
              self.command_search.results = vc;
            });
          }
        }
      }

      let i = this.command_search.resultIndex;
      let max = this.command_search.results.length;
      this.command_search.searchActive = false;
      switch(keyPressed) {
        case 'Escape': {
          this.command_search.searchActive = false;
          break;
        }
        case 'ArrowDown': {
          i = (i + 1) % max;
          this.command_search.cmd = this.command_search.results[i];
        }
        case 'ArrowUp': {
          i -= 1;
          this.command_search.cmd = this.command_search.results[i];
        }
        default: {
          this.command_search.searchActive = true;
          break;
        }
      }

      this.command_search.resultIndex = i;
    },
    select: function (command, hist) {
      if (hist) {
        // If selection is from history, select entire command with arguments
        this.command_search.cmd = command;
      } else {
        // Otherwise, just select command
        this.command_search.cmd = command['name'] + '(';
      }
    },
    searchHist: function () {
      if (this.command_hist.query !== '') {
        this.command_hist.results = this.command_hist.history.filter((c) => c.cmd.toLowerCase().indexOf(this.command_hist.query.toLowerCase()) !== -1);
      } else {
        this.command_hist.results = this.command_hist.history.slice();  // Copy command history into buffer
      }
    },
  },
  computed: {
    reverseCmd: function () {
      return this.command_hist.results.reverse()
    }
  }
});