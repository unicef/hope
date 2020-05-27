import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { InputAdornment, TextField, MenuItem } from '@material-ui/core';
import { Search } from '@material-ui/icons';
import { FlexFieldsTable } from '../../../tables/TargetPopulation/FlexFields';
import { useFlexFieldsQuery } from '../../../../__generated__/graphql';

const TextContainer = styled(TextField)`
  .MuiFilledInput-root {
    border-radius: 4px;
  }
  && {
    width: 65%;
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

const SelectContainer = styled(TextContainer)`
  && {
    width: 33%;
  }
`

const FilterWrapper = styled.div`
  padding: 20px;
  display: flex;
  justify-content: space-between;
`

export function FlexFieldTab() {
  const { data } = useFlexFieldsQuery();
  const [searchValue, setSearchValue] = useState('')
  const [selectOptions, setSelectOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState('');
  useEffect(() => {
    if (data && !selectOptions.length) {
      const options = data.allFieldsAttributes.reduce(function (accumulator, currentValue) {
        if (!accumulator.includes(currentValue.type)) {
          accumulator.push(currentValue.type)
        }
        return accumulator
      }, [])
      setSelectOptions(options)
    }
  }, [data, selectOptions])
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
          onChange={(e) => setSearchValue(e.target.value)}
          value={searchValue}
          InputProps={{
            startAdornment: (
              <InputAdornment position='start'>
                <Search />
              </InputAdornment>
            ),
          }}
        />
        {selectOptions.length &&
          <SelectContainer
            placeholder='Type'
            variant='outlined'
            margin='dense'
            select
            value={selectedOption}
            onChange={(e) => setSelectedOption(e.target.value)}
          >
            {selectOptions.map(type => {
              return <MenuItem key={type} value={type}>{type}</MenuItem>
            })}
          </SelectContainer>
        }
      </FilterWrapper>
      <FlexFieldsTable fields={data.allFieldsAttributes} />
    </>
  )
}