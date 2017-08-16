Vue.component('command-search', {
  template: ' \
      <div class="command-search"> \
        <input \
          class="cmd-input" \
          type="text" \
          v-model="commandQuery" \
          @focus="toggleResults(true)" \
          @blur="toggleResults(false)" \
          @keyup="navigateResults" \
          placeholder="Enter command"> \
        <ul class="cmd-results"\
            v-if="showResults"> \
          <li \
            v-for="command in results"> \
            <p>{{ command["name"] }}</p> \
          </li> \
        </ul> \
      </div> \
    ',
  data: function () {
    return {
      commandQuery: '',
      results: [],
      showResults: false
    }
  },
  methods: {
    toggleResults: function (show) {
      if (show) {
        this.showResults = true;
      } else {
        this.showResults = false;
      }
    },
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
    searchCommand: function(query) {
      self = this;  // Avoid 'this' scoping issues inside .then of promise
      self.getCommands().then(function (vc) {
        self.results = vc.filter((c) => c['name'].toLowerCase()  // Make cmds case insensitive
                                                 .indexOf(query.toLowerCase()  // Make query case insensitive
                                                               .split('(')[0]) !== -1);  // Only search name
      })
    },
    navigateResults: function (event) {
      // Always search
      this.searchCommand(this.commandQuery);
      let keyPressed = event.key;
      // alert(keyPressed);
      switch (keyPressed) {
        case 'Escape': {
          this.showResults = false;
          break;
        }
      }
    }
  }
})

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

      let cmdToSend = this.command_search.cmd;

      // function validCheck(cmdToCheck) {
      //   // Command won't leave client unless this is true
      //   if (this.command_search.results.length != 1) {
      //     // Either no commands found or name matches too many commands
      //     return false;
      //   } else if (cmdToCheck.indexOf('(') == -1) {
      //     return false;
      //   }

      //   return true;
      // }

      // function cleanCmd(cmdToClean) {
      //   // Command can leave client after formatted for server
      //   cmdToClean = cmdToClean.trim();
      //   let endParenthIndex = cmd.indexOf(')');
      //   if (endParenthIndex == -1) {
      //     // Tag on end parentheses 
      //     cmdToClean += ')';
      //   } else {
      //     // If end parentheses are found, then cut off command afterwards
      //     cmdToClean = cmdToClean.substring(0, endParenthIndex + 1);
      //   }

      //   cmdToClean.split(',').filter((c) => c != '').join(',');

      //   return cmdToClean
      // }

      // if (validCheck(cmdToSend)) {
        this.command_search.cmd = cmdToSend;
        // this.socket.send(this.command_search.cmd);
        this.command_hist.history.push({
          cmd: this.command_search.cmd,
          time: Date()
        });
        this.command_hist.results = this.command_hist.history.slice();
        this.command_search.results = [];  // Clear search
      // }
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