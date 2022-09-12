# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import grpc_email_sender.email_sender_pb2 as email__sender__pb2


class EmailSenderStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendEmail = channel.unary_unary(
                '/email_sender.EmailSender/SendEmail',
                request_serializer=email__sender__pb2.SendEmailRequest.SerializeToString,
                response_deserializer=email__sender__pb2.SendEmailReply.FromString,
                )


class EmailSenderServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendEmail(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EmailSenderServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendEmail': grpc.unary_unary_rpc_method_handler(
                    servicer.SendEmail,
                    request_deserializer=email__sender__pb2.SendEmailRequest.FromString,
                    response_serializer=email__sender__pb2.SendEmailReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'email_sender.EmailSender', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class EmailSender(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendEmail(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/email_sender.EmailSender/SendEmail',
            email__sender__pb2.SendEmailRequest.SerializeToString,
            email__sender__pb2.SendEmailReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
