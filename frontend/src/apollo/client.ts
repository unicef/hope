import ApolloClient from 'apollo-client';
import { ApolloLink } from 'apollo-link';
import { HttpLink } from 'apollo-link-http';
import { GRAPHQL_URL } from '../config';
import {createUploadLink} from  'apollo-upload-client';
import { InMemoryCache } from 'apollo-cache-inmemory';

const link = ApolloLink.from([
    new HttpLink({ uri: GRAPHQL_URL }),
    createUploadLink()
    ]);

export const client = new ApolloClient({
    cache: new InMemoryCache(),
    link,
});