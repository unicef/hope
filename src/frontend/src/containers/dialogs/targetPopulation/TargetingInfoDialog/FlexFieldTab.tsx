import { Box, Grid, MenuItem } from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { useAllFieldsAttributesQuery } from '@generated/graphql';
import { FlexFieldsTable } from '../../../tables/targeting/TargetPopulation/FlexFields';

export function FlexFieldTab(): React.ReactElement {
  const { t } = useTranslation();
  const { data } = useAllFieldsAttributesQuery();
  const [searchValue, setSearchValue] = useState('');
  const [selectOptions, setSelectOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState('All');
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
        <Grid item xs={3}>
          <SearchTextField
            label={t('Search')}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </Grid>
        <Grid item xs={3}>
          {selectOptions.length && (
            <SelectFilter
              onChange={(e) => setSelectedOption(e.target.value)}
              variant="outlined"
              label={t('Type')}
              value={selectedOption}
              fullWidth
              disableClearable
            >
              <MenuItem value="All">
                <em>{t('All')}</em>
              </MenuItem>
              {selectOptions.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </SelectFilter>
          )}
        </Grid>
        <Grid item xs={3}>
          <SelectFilter
            onChange={(e) => setSelectedFieldType(e.target.value)}
            label={t('Field Type')}
            value={selectedFieldType}
            fullWidth
            disableClearable
          >
            <MenuItem value="All">
              <em>{t('All')}</em>
            </MenuItem>
            {[
              { name: 'Flex field', value: 'Flex field' },
              { name: 'Core field', value: 'Core field' },
            ].map((el) => (
              <MenuItem key={el.name} value={el.value}>
                {el.name}
              </MenuItem>
            ))}
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
}
