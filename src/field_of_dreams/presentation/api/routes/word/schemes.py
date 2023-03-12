from marshmallow import Schema, fields


class WordResponseSchema(Schema):
    id = fields.Int(required=True)
    word = fields.Str(required=True)
    question = fields.Str(required=True)


class CreateWordRequestSchema(Schema):
    word = fields.Str(required=True)
    question = fields.Str(required=True)


class UpdateWordRequestSchema(Schema):
    id = fields.Int(required=True)
    word = fields.Str(required=True)
    question = fields.Str(required=True)


class DeleteWordRequestSchema(Schema):
    id = fields.Int(required=True)


class GetWordRequestSchema(Schema):
    word = fields.Str(required=True)


class GetWordResponseSchema(Schema):
    words = fields.Nested(WordResponseSchema, many=True)
