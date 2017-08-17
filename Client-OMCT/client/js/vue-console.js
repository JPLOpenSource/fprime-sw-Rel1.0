var command = {
  props: ['showResults', 'socket'],
  template: `
    <div class="command-search">
      <input type="text"
             class="cmd-input"
             v-model="commandQuery"
             @keyup="navigateResults"
             placeholder="Enter command"
             ref="input">
      <ul class="cmd-results"
          v-show="showResults">
        <li v-for="command in results"
            @click="select(command)">
          <p>{{ command["name"] }}</p>
        </li>
      </ul>
    </div>
  `,
  data: function () {
    return {
      commandQuery: '',
      results: [],
      freezeResults: false,
      warning: ''
    }
  },
  watch: {
    commandQuery: function(val) {
      this.searchCommand(val);
    },
    showResults: function() {
      this.searchCommand(this.commandQuery);
    },
  },
  methods: {
    getCommands: function () {
      // Returns promise of array of all commands
      return getDictionary().then(function (dict) {
        let commandDict = dict['isf']['commands'];       
        let validCommands = [];
        for (id in commandDict) {
          validCommands.push(commandDict[id]);
        }
        return validCommands;
      });
    },
    select: function (cmd) {
      this.commandQuery = cmd["name"] + ': ';
      this.freezeResults = true;
      this.$refs.input.focus();
    },
    searchCommand: function(query) {
      self = this;  // Avoid 'this' scoping issues inside .then of promise
      self.getCommands().then(function (vc) {
        self.results = vc.filter((c) => c['name'].toLowerCase()  // Make cmds case insensitive
                                                 .indexOf(query.toLowerCase()  // Make query case insensitive
                                                               .split(':')[0]) !== -1);  // Only search name
      });
    },
    cleanCommand: function(cmd) {
      cmd.split(',').filter((char) => char != '').join(','); // Remove extra commas and whitespace
    },
    parseCmd: function(cmd) {
      if (this.results.length != 1) {
        this.warning = 'Invalid command name!';
        return false;
      }
      if (cmd.indexOf(':') == -1) {
        this.warning = 'Please add colon ( : ) to the end of the command name!';
        return false;
      }

      let argsInput = cmd.substring(cmd.indexOf(':') + 1).split(',').filter((c) => c != '');  // Get arguments

      let commandReq = this.results[0]; // Get command info to check arguments with

      if (commandReq['arguments'].length != argsInput.length) {
        this.warning = 'Not enough Args!';
        return false;
      }

      userArgs = [];
      commandReq['arguments'].forEach(function (aR, i) {
        let typeReq = aR['type'];

        let userA;
        if (typeReq != 'String') {
          userA = parseInt(argsInput[i]);
          if (userA == NaN) {
            this.warning = 'Expected a numerical number for argument ' + i.toString();
            return false;
          }
        }
        // DEV More checks
        userArgs.push(userA);
      });

      return {
        'id': commandReq['id'],
        'arguments': userArgs,
        'timestamp': Date.now()
      };
    },
    sendCommand: function(cmd) {
      commandToSend = this.parseCmd(cmd);
      alert(this.warning);
      if (commandToSend) {

        this.socket.send(commandToSend);
      }
    },
    navigateResults: function (event) {
      // Always search
      this.freezeResults = false;
      let keyPressed = event.key;
      // alert(keyPressed);
      switch (keyPressed) {
        case 'Escape': {
          this.showResults = false;
          break;
        }
        case 'Enter': {
          this.sendCommand(this.commandQuery);
          break;
        }
      }
    }
  }
}

var hist = {
  template: `
    <div class="command-hist">
      <ul class="hist-results">
        <li v-for="command in commandHistory">
          <p>{{ command }}</p>
        </li>
      </ul>

      <input
        class="hist-input" 
        type="text"
        v-model="historyQuery"
        placeholder="Search history">
    </div>
  `,
  data: function () {
    return {
      commandHistory: 'sdjsijdisadiasjdasdsadsadsasadasdasdsadsadsadsadsadsadsadsadsadsadsadsadsa'.split(''),
      historyQuery: ''
    }
  }
};

var CommandView = Vue.extend({
  template: $('#commandTemplate').text(),
  components: {
    'command': command,
    'history': hist
  },
  methods: {
    toggleSearch: function (show) {
      this.showCmdSearchResults = show;
    }
  }
})
