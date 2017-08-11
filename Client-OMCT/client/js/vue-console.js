
var CommandView = Vue.extend({
  template: $('#commandTemplate').text(),
  data: function () {
    return {
      command_search: {
        searchActive: true,
        cmd: '',
        results: []
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
      // socket.send(this.command_search.cmd);
      this.command_hist.history.push({
        cmd: this.command_search.cmd,
        time: Date()
      });
      this.command_hist.results = this.command_hist.history.slice();
      this.command_search.results = [];  // Clear search
    },
    searchCmd: function (event) {
      let keyPressed = event.key;
      if (this.command_search.cmd !== '') {
        console.log(event.key);

        self = this;  // Avoid 'this' scoping issues inside .then of promise
        self.getCommands().then(function (vc) {
          self.command_search.results = vc.filter((c) => c['name'].toLowerCase().indexOf(self.command_search.cmd.toLowerCase()) !== -1);
        });

      } else {
        this.command_search.results = [];
        if (keyPressed == 'ArrowDown') {
          self = this;
          self.getCommands().then(function (vc) {
            self.command_search.results = vc;
          });
        }
      }

      switch(event.key) {
        case 'Escape': 
          this.command_search.searchActive = false;
          break;
        
      }
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