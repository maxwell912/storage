from Client import Client

client = Client()


def get_commands(client=client):
    print("""add key value
get key
rm key""")
    while True:
        print('\nPrint next command')
        command = input()

        if command.startswith('add'):
            command = command.split(' ')
            client.add(command[1], ' '.join(command[2:]))

        elif command.startswith('get'):
            command = command.split(' ')
            print(client.get(command[1]))

        elif command.startswith('rm'):
            command = command.split(' ')
            client.remove(command[1])
