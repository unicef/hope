import { MenuItem, Select } from '@material-ui/core';
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useAllLocationsQuery } from '../__generated__/graphql';
import { getCurrentLocation } from '../utils/utils';

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

export function CountryCombo() {
  const { data } = useAllLocationsQuery({ fetchPolicy: 'cache-and-network' });
  const [value, setValue] = useState(getCurrentLocation());
  const history = useHistory();
  const onChange = (e): void => {
    localStorage.setItem('LocationId', e.target.value);
    setValue(e.target.value);
    history.push('/');
  };
  if (!data) {
    return null;
  }
  return (
    <CountrySelect variant='filled' value={value} onChange={onChange}>
      {data.allLocations.edges.map((each) => (
        <MenuItem key={each.node.id} value={each.node.id}>
          {each.node.country}
        </MenuItem>
      ))}
    </CountrySelect>
  );
}
