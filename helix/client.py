class HelixClient:
    """
    This class serves as a direct processor for sending and receiving queries and query respones
    to and from a helixdb instance.
    """
    def __init__(self, h_server: str="https://localhost:6969"):
        self.h_server = h_server


# idea: have a custom Query class that you can extend, so we have a couple default ones,
# but then you can just write you're own and integrate them based on your datatype, endpoint
# query type/structure etc.