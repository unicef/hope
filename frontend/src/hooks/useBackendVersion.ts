import { useQuery } from '@apollo/react-hooks';
import { gql } from 'apollo-boost';

const GET_BACKEND_VERSION = gql`
  {
    backendVersion @client
  }
`;

export const useBackendVersion = (): string => {
  const { data, loading } = useQuery(GET_BACKEND_VERSION, {
    fetchPolicy: 'cache-only',
  });

  if (loading) {
    return null;
  }

  return data.backendVersion;
};
