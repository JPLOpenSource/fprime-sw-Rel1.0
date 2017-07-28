import sys
import zmq
import pickle
import click

@click.group()
def cli():
    """
    CLI Utility to command and monitor the ZmqServer.
    """

class ClientModel(object):
    def __init__(self):
        self.__flight_clients = {}
        self.__ground_clients = {}
    def SetClientSubscriptions(self, client_sub_dict):
        self.__flight_clients = client_sub_dict['flight']
        self.__ground_clients = client_sub_dict['ground']

    def SetFlightClientSubscriptions(self, client_dict):
        self.__flight_clients = client_dict

    def SetGroundClientSubscriptions(self, client_dict):
        self.__ground_clients = client_dict

    def GetFlightClientSubscriptions(self, name):
        return self.__flight_clients[name]

    def GetGroundClientSubscriptions(self, name):
        return self.__ground_clients[name]

    def GetFlightClientNames(self):
        return self.__flight_clients.keys()

    def GetGroundClientNames(self):
        return self.__ground_clients.keys()

    def VerifyClientName(self, client_name):
        if client_name in self.__flight_clients:
            return 'flight' 
        elif client_name in self.__ground_clients:
            return 'ground' 
        else:
            return None 

    def VerifyPubList(self, pub_string):
        pub_list = pub_string.split(',')
        for client in pub_list:
            if self.VerifyClientName(client) is None:
                return None 

        return pub_list

class Connection(object):
    def __init__(self, port, address):
        self.__context = zmq.Context()
        self.__cmd_socket = self.__context.socket(zmq.DEALER) 
        self.__cmd_socket.setsockopt(zmq.RCVTIMEO, 200)
        self.__cmd_socket.setsockopt(zmq.LINGER, 0)
        self.__cmd_socket.connect("tcp://{}:{}".format(address, port))

    def GetSubscriptions(self):
        self.__cmd_socket.send_multipart([b"LIST"])

        try:
            msg = self.__cmd_socket.recv_multipart() 
            client_sub_dict = pickle.loads(msg[0])
            return client_sub_dict 

        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                click.echo("List Subcriptions response timeout")
                return None

    def SubscribeClientTo(self, client_name, client_type, pub_list):
        self.ConfigureClientSubscription(client_name, client_type, pub_list, "SUB") 
    def UnsubscribeClientFrom(self, client_name, client_type, pub_list):
        self.ConfigureClientSubscription(client_name, client_type, pub_list, "USUB") 

    def ConfigureClientSubscription(self, client_name, client_type, pub_list, option):
        for pub_client in pub_list:
            self.__cmd_socket.send_multipart([option.encode(), client_name.encode(),\
                                              client_type.encode(), pub_client.encode()])


    def Close(self):
        self.__cmd_socket.close()
        self.__context.term()

def n_NewLines(n):
    for i in range(n):
        click.echo('')

def ResetDisplay(client_model, connection):
        click.clear()

        csd = connection.GetSubscriptions()
        if csd is not None:
            client_model.SetClientSubscriptions(csd)

        click.echo('Flight Clients')
        n_NewLines(1)
        for client_name in client_model.GetFlightClientNames():

            click.echo('{} Subscribed To'.format(client_name)) 
            # Iterate through and display flight client subscriptions
            for g_client in client_model.GetFlightClientSubscriptions(client_name):
                click.echo("-->{}".format(g_client))

            n_NewLines(1)


        n_NewLines(3) 
        click.echo('Ground Clients')
        n_NewLines(1)
        for client_name in client_model.GetGroundClientNames():
            
            click.echo('{} Subscribed To'.format(client_name))
            # Iterate through and display ground client subscriptions
            for f_client in client_model.GetGroundClientSubscriptions(client_name):
                click.echo("-->{}".format(f_client))
            n_NewLines(1)



@cli.command()
@click.argument('port')
@click.argument('server_address')
def main(port, server_address):
    """
    Starts the utility.
    """
 
    client_model = ClientModel()
    connection   = Connection(port, server_address)

    menu = 'main'
    while(1):
        ResetDisplay(client_model, connection)
        n_NewLines(3)
 
        if menu == 'main':
            click.echo('Main Menu')
            click.echo("'''''''''")
            click.echo('s: Subscribe Client')
            click.echo('u: Unsubscribe Client')
            click.echo('q: Quit')
            

            char = click.getchar() 
    
            if char == 's':
                menu = 'subscribe'
            elif char == 'u':
                menu = 'unsubscribe' 
            elif char == 'q':
                menu = 'quit'
            else:
                click.echo('Invalid Input')
            
            continue
 

        elif menu == 'subscribe':
            click.echo("Subscribe Menu")
            click.echo("''''''''''''''")
            click.echo("<return>: Continue")
            click.echo("q: Return")
            if(click.getchar() == 'q'):
                menu = 'main'
                continue

            client_name= click.prompt('Subscriber Name')
            client_type = client_model.VerifyClientName(client_name)
            if client_type is not None:
                ResetDisplay(client_model, connection)
                click.echo('Enter clients for {} to subscribe to.'.format(client_name))
                pub_list = click.prompt("Seperated by commas") 
                pub_list = client_model.VerifyPubList(pub_list)
                if pub_list is not None:            
                    connection.SubscribeClientTo(client_name, client_type, pub_list) 
                    menu = 'main'
                else:
                    click.echo("Error parsing: {}".format(pub_list)) 
            else:
                click.echo("Unknown client_name: {}".format(client_name))
                continue

        elif menu == 'unsubscribe':
            click.echo("Unsubscribe Menu")
            click.echo("''''''''''''''''")
            click.echo("<return>: Continue")
            click.echo("q: Return")
            if(click.getchar() == 'q'):
                menu = 'main'
                continue
            client_name = click.prompt("Unsubscriber's Name")
            client_type = client_model.VerifyClientName(client_name)
            if client_type is not None:
                click.echo("Enter clients for {} to unsubscribe to".format(client_name)) 
                pub_list= click.prompt("Seperated by commas")
                pub_list = client_model.VerifyPubList(pub_list)
                if pub_list is not None:
                    connection.UnsubscribeClientFrom(client_name, client_type, pub_list)
                    menu = 'main'
            else:
                click.echo("Unknown client name: {}".format(client_name))
        elif menu == 'quit':
            click.echo("Quit")
            click.clear()
            connection.Close()
            return



if __name__ == '__main__':
    sys.exit(main())
