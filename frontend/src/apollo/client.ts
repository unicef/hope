import ApolloClient from 'apollo-boost';
import { GRAPHQL_URL } from '../config';

export const client = new ApolloClient({
    uri: GRAPHQL_URL,
});