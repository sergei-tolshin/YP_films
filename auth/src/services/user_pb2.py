# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: user.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nuser.proto\x12\x04user\">\n\x0fUserInfoRequest\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x01 \x01(\t\x12\x15\n\rrefresh_token\x18\x02 \x01(\t\"8\n\rUserInfoReply\x12\r\n\x05roles\x18\x01 \x01(\t\x12\x18\n\x10permission_level\x18\x02 \x01(\x05\"\'\n\x0fUserViewRequest\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x01 \x01(\t\"!\n\rUserViewReply\x12\x10\n\x08username\x18\x01 \x01(\t2x\n\x04User\x12\x37\n\x07GetInfo\x12\x15.user.UserInfoRequest\x1a\x13.user.UserInfoReply\"\x00\x12\x37\n\x07GetName\x12\x15.user.UserViewRequest\x1a\x13.user.UserViewReply\"\x00\x62\x06proto3')



_USERINFOREQUEST = DESCRIPTOR.message_types_by_name['UserInfoRequest']
_USERINFOREPLY = DESCRIPTOR.message_types_by_name['UserInfoReply']
_USERVIEWREQUEST = DESCRIPTOR.message_types_by_name['UserViewRequest']
_USERVIEWREPLY = DESCRIPTOR.message_types_by_name['UserViewReply']
UserInfoRequest = _reflection.GeneratedProtocolMessageType('UserInfoRequest', (_message.Message,), {
  'DESCRIPTOR' : _USERINFOREQUEST,
  '__module__' : 'user_pb2'
  # @@protoc_insertion_point(class_scope:user.UserInfoRequest)
  })
_sym_db.RegisterMessage(UserInfoRequest)

UserInfoReply = _reflection.GeneratedProtocolMessageType('UserInfoReply', (_message.Message,), {
  'DESCRIPTOR' : _USERINFOREPLY,
  '__module__' : 'user_pb2'
  # @@protoc_insertion_point(class_scope:user.UserInfoReply)
  })
_sym_db.RegisterMessage(UserInfoReply)

UserViewRequest = _reflection.GeneratedProtocolMessageType('UserViewRequest', (_message.Message,), {
  'DESCRIPTOR' : _USERVIEWREQUEST,
  '__module__' : 'user_pb2'
  # @@protoc_insertion_point(class_scope:user.UserViewRequest)
  })
_sym_db.RegisterMessage(UserViewRequest)

UserViewReply = _reflection.GeneratedProtocolMessageType('UserViewReply', (_message.Message,), {
  'DESCRIPTOR' : _USERVIEWREPLY,
  '__module__' : 'user_pb2'
  # @@protoc_insertion_point(class_scope:user.UserViewReply)
  })
_sym_db.RegisterMessage(UserViewReply)

_USER = DESCRIPTOR.services_by_name['User']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _USERINFOREQUEST._serialized_start=20
  _USERINFOREQUEST._serialized_end=82
  _USERINFOREPLY._serialized_start=84
  _USERINFOREPLY._serialized_end=140
  _USERVIEWREQUEST._serialized_start=142
  _USERVIEWREQUEST._serialized_end=181
  _USERVIEWREPLY._serialized_start=183
  _USERVIEWREPLY._serialized_end=216
  _USER._serialized_start=218
  _USER._serialized_end=338
# @@protoc_insertion_point(module_scope)
