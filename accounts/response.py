from graphql import GraphQLError


ERROR_RESPONSE = GraphQLError('AuthenticationError', extensions={
    'code': 401,
    'name': 'UNAUTHENTICATED',
    'message': 'Authentication Error',
})
