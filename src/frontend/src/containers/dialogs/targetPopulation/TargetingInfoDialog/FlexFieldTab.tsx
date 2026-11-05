import Box from '@mui/material/Box';
import { MenuItem, TableContainer } from '@mui/material';
import type { ReactElement } from 'react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SearchTextField } from '@components/core/SearchTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { FlexFieldsTable } from '../../../tables/targeting/TargetPopulation/FlexFields';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { restQueryKey } from '@utils/queryKeys';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

export function FlexFieldTab(): ReactElement {
  const { t } = useTranslation();
  const { businessArea, isAllPrograms } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const { data } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasAllFieldsAttributesList,
      {
        slug: businessArea,
        programId: selectedProgram?.id,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasAllFieldsAttributesList({
        slug: businessArea,
        programId: selectedProgram?.id,
      }),
    enabled: !!selectedProgram?.id && !isAllPrograms, // Ensure the query runs only when programId is available
  });
  const [searchValue, setSearchValue] = useState('');
  const [selectOptions, setSelectOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState('All');
  const [selectedFieldType, setSelectedFieldType] = useState('All');
  useEffect(() => {
    // restBusinessAreasAllFieldsAttributesList returns a bare array, not a paginated page.
    if (data?.length && !selectOptions.length) {
      const options = data.map((el) => el.associatedWith);
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
    <Box sx={{ p: 3 }}>
      <ResponsiveGridContainer spacing={3}>
        <ResponsiveGrid size="quarter">
          <SearchTextField
            label={t('Search')}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            data-cy="filters-search"
            fullWidth
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
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
        </ResponsiveGrid>
      </ResponsiveGridContainer>
      <TableContainer>
        <FlexFieldsTable
          selectedOption={selectedOption}
          searchValue={searchValue}
          selectedFieldType={selectedFieldType}
          fields={data}
        />
      </TableContainer>
    </Box>
  );
}
