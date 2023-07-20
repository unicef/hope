import { MenuItem, Select } from '@material-ui/core';
import React from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useAllProgramsForChoicesQuery } from '../__generated__/graphql';
import { LoadingComponent } from '../components/core/LoadingComponent';
import { useBaseUrl } from '../hooks/useBaseUrl';

const CountrySelect = styled(Select)`
  && {
    width: ${({ theme }) => theme.spacing(58)}px;
    background-color: rgba(104, 119, 127, 0.5);
    color: #e3e6e7;
    border-bottom-width: 0;
    border-radius: 4px;
    height: 40px;
  }
  .MuiFilledInput-input {
    padding: 0 10px;
    background-color: transparent;
  }
  .MuiSelect-select:focus {
    background-color: transparent;
  }
  .MuiSelect-icon {
    color: #e3e6e7;
  }
  &&:hover {
    border-bottom-width: 0;
    border-radius: 4px;
  }
  &&:hover::before {
    border-bottom-width: 0;
  }
  &&::before {
    border-bottom-width: 0;
  }
  &&::after {
    border-bottom-width: 0;
  }
  &&::after:hover {
    border-bottom-width: 0;
  }
`;

export const GlobalProgramSelect = (): React.ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const history = useHistory();
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea, first: 100 },
    fetchPolicy: 'cache-and-network',
  });

  const onChange = (e): void => {
    if (e.target.value === 'all') {
      history.push(`/${businessArea}/programs/${e.target.value}/list`);
    } else {
      history.push(
        `/${businessArea}/programs/${e.target.value}/details/${e.target.value}`,
      );
    }
  };
  if (loading) {
    return <LoadingComponent />;
  }
  if (!data) {
    return null;
  }

  return (
    <CountrySelect
      data-cy='global-program-filter'
      variant='filled'
      value={programId}
      onChange={onChange}
    >
      <MenuItem key='all' value='all'>
        All Programmes
      </MenuItem>
      {data.allPrograms.edges.map((each) => (
        <MenuItem key={each.node.id} value={each.node.id}>
          {each.node.name}
        </MenuItem>
      ))}
    </CountrySelect>
  );
};
