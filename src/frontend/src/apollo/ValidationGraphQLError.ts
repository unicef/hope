import { GraphQLError } from 'graphql';

export class ValidationGraphQLError extends GraphQLError {
  validationErrors;
}
