import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { InputAdornment, TextField, MenuItem, FormControl } from '@material-ui/core';
import { Search } from '@material-ui/icons';
import { FlexFieldsTable } from '../../../tables/TargetPopulation/FlexFields';
import { useFlexFieldsQuery } from '../../../../__generated__/graphql';
import InputLabel from '../../../../shared/InputLabel';
import Select from '../../../../shared/Select';

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

const FilterWrapper = styled.div`
  padding: 20px;
  display: flex;
  justify-content: space-between;
`;

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

export function FlexFieldTab() {
  const { data } = useFlexFieldsQuery();
  const [searchValue, setSearchValue] = useState('')
  const [selectOptions, setSelectOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState('');
  useEffect(() => {
    if (data && !selectOptions.length) {
      const options = data.allGroupsWithFields.reduce(function (accumulator, currentValue) {
        currentValue.flexAttributes.map(function(each) {
          return !accumulator.includes(each.associatedWith) ? accumulator.push(each.associatedWith) : null
        })
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
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Type</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => setSelectedOption(e.target.value)}
              variant='outlined'
              label='Type'
              value={selectedOption}
            >
              <MenuItem value=''>
                <em>All</em>
              </MenuItem>
              {selectOptions.map(type => {
                return <MenuItem key={type} value={type}>{type}</MenuItem>
              })}
            </Select>
          </StyledFormControl>
        }
      </FilterWrapper>
      <FlexFieldsTable selectedOption={selectedOption} searchValue={searchValue} fields={data.allGroupsWithFields} />
    </>
  )
}