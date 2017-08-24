from pubsub_pair import PubSubPair

if __name__ == "__main__":
    ps = PubSubPair("tester", "ipc:///tmp/pipe.4999",\
                "ipc:///tmp/pipe.5000",\
                "ipc:///tmp/pipe.5001",\
                "ipc:///tmp/pipe.5002",\
                "ipc:///tmp/pipe.5003",\
                "ipc:///tmp/pipe.5004")

    ps.start()
