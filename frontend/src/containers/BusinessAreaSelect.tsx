import { MenuItem, Select } from '@mui/material';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useCachedMe } from '@hooks/useCachedMe';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useApolloClient } from '@apollo/client';

const CountrySelect = styled(Select)`
  && {
    width: ${({ theme }) => theme.spacing(58)};
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

export function BusinessAreaSelect(): React.ReactElement {
  const { data } = useCachedMe();
  const { businessArea } = useBaseUrl();
  const navigate = useNavigate();
  const client = useApolloClient();

  const onChange = async (e): Promise<void> => {
    await client.cache.reset();
    navigate(`/${e.target.value}/programs/all/list`);
  };

  if (!data) {
    return null;
  }
  return (
    <CountrySelect variant="filled" value={businessArea} onChange={onChange}>
      {data.me.businessAreas.edges.map((each) => (
        <MenuItem key={each.node.slug} value={each.node.slug}>
          {each.node.name}
        </MenuItem>
      ))}
    </CountrySelect>
  );
}
