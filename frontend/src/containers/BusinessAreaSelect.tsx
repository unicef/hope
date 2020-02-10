import { MenuItem, Select } from '@material-ui/core';
import React from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useAllBusinessAreasQuery, useMeQuery } from '../__generated__/graphql';
import { useBusinessArea } from '../hooks/useBusinessArea';

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

export function BusinessAreaSelect() {
  const { data } = useMeQuery({
    fetchPolicy: 'cache-and-network',
  });
  const businessArea = useBusinessArea();
  const history = useHistory();
  const onChange = (e): void => {
    history.push(`/${e.target.value}`);
  };
  if (!data) {
    return null;
  }
  return (
    <CountrySelect variant='filled' value={businessArea} onChange={onChange}>
      {data.me.businessAreas.edges.map((each) => (
        <MenuItem key={each.node.slug} value={each.node.slug}>
          {each.node.name}
        </MenuItem>
      ))}
    </CountrySelect>
  );
}
