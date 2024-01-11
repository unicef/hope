import { useQuery } from '@apollo/react-hooks';
import { gql } from 'apollo-boost';
import { useEffect, useState } from 'react';

const GET_BACKEND_VERSION = gql`
  {
    backendVersion
  }
`;

export const useBackendVersion = (): string => {
  const { data } = useQuery(GET_BACKEND_VERSION, {
    fetchPolicy: 'cache-only',
  });
  const [version, setVersion] = useState<string>('');

  useEffect(() => {
    if (data?.backendVersion) {
      setVersion(data.backendVersion);
    }
  }, [data]);

  return version;
};
