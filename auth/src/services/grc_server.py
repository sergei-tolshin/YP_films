from concurrent import futures

import grpc
import jwt

import user_pb2
import user_pb2_grpc
from core.config import JWT_SECRET_KEY


class User(user_pb2_grpc.UserServicer):

    def GetName(self, request, context) -> str | None:
        """Get username from jwt token."""
        try:
            decode = jwt.decode(request.access_token, JWT_SECRET_KEY, algorithms="HS256")
        except jwt.exceptions.PyJWTError:
            return user_pb2.UserViewReply(username=None)
        return user_pb2.UserViewReply(username=decode["sub"])


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServicer_to_server(User(), server)
    server.add_insecure_port('[::]:50055')
    server.start()
    server.wait_for_termination()
