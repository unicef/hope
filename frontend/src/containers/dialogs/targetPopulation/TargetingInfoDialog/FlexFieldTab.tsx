import React from 'react';
import styled from 'styled-components';
import { InputAdornment, TextField } from '@material-ui/core';
import { Search } from '@material-ui/icons';
import { FlexFieldsTable } from '../../../tables/TargetPopulation/FlexFields';
import { useFlexFieldsQuery } from '../../../../__generated__/graphql';

const TextContainer = styled(TextField)`
  .MuiFilledInput-root {
    border-radius: 4px;
  }
  && {
    width: 232px;
    color: #5f6368;
    border-bottom: 0;
  }
  .MuiFilledInput-underline:before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline:before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline:hover {
    border-bottom: 0;
    border-radius: 4px;
  }
  .MuiFilledInput-underline:hover::before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::before {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::after {
    border-bottom: 0;
  }
  .MuiFilledInput-underline::after:hover {
    border-bottom: 0;
  }
  .MuiSvgIcon-root {
    color: #5f6368;
  }
  .MuiFilledInput-input {
    padding: 10px 15px 10px;
  }
  .MuiInputAdornment-filled.MuiInputAdornment-positionStart:not(.MuiInputAdornment-hiddenLabel) {
    margin: 0px;
  }
`;

const FilterWrapper = styled.div`
  padding: 20px;
  display: flex;
`

export function FlexFieldTab() {
  const { data } = useFlexFieldsQuery();
  if (!data) {
    return null;
  }
  return (
    <>
      <FilterWrapper>
        <TextContainer
          placeholder='Search'
          variant='outlined'
          margin='dense'
          //onChange={(e) => handleFilterChange(e, 'name')}
          InputProps={{
            startAdornment: (
              <InputAdornment position='start'>
                <Search />
              </InputAdornment>
            ),
          }}
        />
        <TextContainer
          placeholder='Search'
          variant='outlined'
          margin='dense'
          //onChange={(e) => handleFilterChange(e, 'name')}
          InputProps={{
            startAdornment: (
              <InputAdornment position='start'>
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </FilterWrapper>
      <FlexFieldsTable fields={data.allFieldsAttributes} />
    </>
  )
}