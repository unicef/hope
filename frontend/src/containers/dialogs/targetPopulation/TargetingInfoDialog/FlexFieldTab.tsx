import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import {
  InputAdornment,
  TextField,
  MenuItem,
  FormControl,
  Grid,
} from '@material-ui/core';
import { Search } from '@material-ui/icons';
import { FlexFieldsTable } from '../../../tables/TargetPopulation/FlexFields';
import { useAllFieldsAttributesQuery } from '../../../../__generated__/graphql';
import InputLabel from '../../../../shared/InputLabel';
import Select from '../../../../shared/Select';

const TextContainer = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`;

const StyledFormControl = styled(FormControl)`
  width: 232px;
  color: #5f6368;
  border-bottom: 0;
`;

const FilterWrapper = styled.div`
  padding: 20px;
`;

export function FlexFieldTab(): React.ReactElement {
  const { data } = useAllFieldsAttributesQuery();
  const [searchValue, setSearchValue] = useState('');
  const [selectOptions, setSelectOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState('');
  const [selectedFieldType, setSelectedFieldType] = useState('All');
  useEffect(() => {
    if (data && !selectOptions.length) {
      const options = data.allFieldsAttributes.map((el) => el.associatedWith);
      const filteredOptions = options.filter(
        (item, index) => options.indexOf(item) === index,
      );
      setSelectOptions(filteredOptions);
    }
  }, [data, selectOptions]);
  if (!data) {
    return null;
  }

  return (
    <FilterWrapper>
      <Grid container spacing={3}>
        <Grid item>
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
        </Grid>
        <Grid item>
          {selectOptions.length && (
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
                {selectOptions.map((type) => {
                  return (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  );
                })}
              </Select>
            </StyledFormControl>
          )}
        </Grid>
        <Grid item>
          <StyledFormControl variant='outlined' margin='dense'>
            <InputLabel>Field Type</InputLabel>
            <Select
              /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
              // @ts-ignore
              onChange={(e) => setSelectedFieldType(e.target.value)}
              variant='outlined'
              label='Field Type'
              value={selectedFieldType}
            >
              <MenuItem value='All'>
                <em>All</em>
              </MenuItem>
              {[
                { name: 'Flex field', value: 'Flex field' },
                { name: 'Core field', value: 'Core field' },
              ].map((el) => {
                return (
                  <MenuItem key={el.name} value={el.value}>
                    {el.name}
                  </MenuItem>
                );
              })}
            </Select>
          </StyledFormControl>
        </Grid>
      </Grid>
      <FlexFieldsTable
        selectedOption={selectedOption}
        searchValue={searchValue}
        selectedFieldType={selectedFieldType}
        fields={data.allFieldsAttributes}
      />
    </FilterWrapper>
  );
}
