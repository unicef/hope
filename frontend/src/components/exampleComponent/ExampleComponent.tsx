import React from 'react';
import { useAllProgramsQuery } from '../../__generated__/graphql';

export const ExampleComponent = () => {
  const { data, loading, error } = useAllProgramsQuery({
    variables: {
      businessArea: 'afghanistan',
    },
  });

  if (loading) {
    return null;
  }

  return <div>{data.allPrograms.totalCount}</div>;
};
