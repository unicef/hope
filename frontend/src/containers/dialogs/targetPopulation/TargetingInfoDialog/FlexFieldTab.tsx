import { Box, Grid, MenuItem } from '@material-ui/core';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SearchTextField } from '../../../../components/core/SearchTextField';
import { SelectFilter } from '../../../../components/core/SelectFilter';
import { useAllFieldsAttributesQuery } from '../../../../__generated__/graphql';
import { FlexFieldsTable } from '../../../tables/targeting/TargetPopulation/FlexFields';

export const FlexFieldTab = (): React.ReactElement => {
  const { t } = useTranslation();
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
    <Box p={3}>
      <Grid container spacing={3}>
        <Grid item>
          <SearchTextField
            label={t('Search')}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            data-cy='filters-search'
          />
        </Grid>
        <Grid item>
          {selectOptions.length && (
            <SelectFilter
              onChange={(e) => setSelectedOption(e.target.value)}
              variant='outlined'
              label={t('Type')}
              value={selectedOption}
            >
              <MenuItem value=''>
                <em>{t('All')}</em>
              </MenuItem>
              {selectOptions.map((type) => {
                return (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                );
              })}
            </SelectFilter>
          )}
        </Grid>
        <Grid item>
          <SelectFilter
            onChange={(e) => setSelectedFieldType(e.target.value)}
            label={t('Field Type')}
            value={selectedFieldType}
          >
            <MenuItem value={t('All')}>
              <em>{t('All')}</em>
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
          </SelectFilter>
        </Grid>
      </Grid>
      <FlexFieldsTable
        selectedOption={selectedOption}
        searchValue={searchValue}
        selectedFieldType={selectedFieldType}
        fields={data.allFieldsAttributes}
      />
    </Box>
  );
};
