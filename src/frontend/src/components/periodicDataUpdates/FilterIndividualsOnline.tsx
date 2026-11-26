import { DatePickerFilter } from '@components/core/DatePickerFilter';
import { FiltersSection } from '@components/core/FiltersSection';
import { NumberTextField } from '@components/core/NumberTextField';
import { SelectFilter } from '@components/core/SelectFilter';
import { MenuItem } from '@mui/material';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import { YES_NO_CHOICES } from '@utils/constants';
import { RdiAutocompleteRestFilter } from '@shared/autocompletes/RdiAutocompleteRestFilter';
import { useSexChoices } from '@hooks/useSexChoices';
import { AdminAreaAutocompleteMultipleRestFilter } from '@shared/autocompletes/rest/AdminAreaAutocompleteMultipleRestFilter';
import { TargetPopulationAutocompleteRestFilter } from '@shared/autocompletes/rest/TargetPopulationAutocompleteRestFilter';
import { t } from 'i18next';
import type { FC } from 'react';

interface FilterIndividualsOnlineProps {
  filter;
  setFilter: (filter) => void;
  isOnPaper: boolean;
}

export const FilterIndividualsOnline: FC<FilterIndividualsOnlineProps> = ({
  filter,
  setFilter,

  isOnPaper = true,
}) => {
  const { data: sexChoices } = useSexChoices();

  const handleStateFilterChange = (name, value) => {
    setFilter((prevFilter) => ({
      ...prevFilter,
      [name]: value,
    }));
  };

  return (
    <FiltersSection isOnPaper={isOnPaper} withApplyClearButtons={false}>
      <ResponsiveGridContainer
        spacing={3}
        sx={{
          alignItems: 'flex-end',
        }}
      >
        <ResponsiveGrid size="quarter">
          <RdiAutocompleteRestFilter
            value={filter.registrationDataImportId}
            onChange={(selectedItem) =>
              handleStateFilterChange('registrationDataImportId', selectedItem)
            }
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <TargetPopulationAutocompleteRestFilter
            value={filter.targetPopulationId}
            onChange={(selectedItem) =>
              handleStateFilterChange('targetPopulationId', selectedItem)
            }
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) => handleStateFilterChange('gender', e.target.value)}
            label={t('Gender')}
            value={filter.gender}
            data-cy="ind-filters-gender"
          >
            {sexChoices?.map((each) => (
              <MenuItem key={each.value} value={each.value}>
                {t(each.name)}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <NumberTextField
            topLabel={t('Age')}
            value={filter.ageFrom}
            placeholder={t('From')}
            fullWidth
            onChange={(e) => handleStateFilterChange('ageFrom', e.target.value)}
            data-cy="hh-filters-age-from"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <NumberTextField
            value={filter.ageTo}
            placeholder={t('To')}
            fullWidth
            onChange={(e) => handleStateFilterChange('ageTo', e.target.value)}
            data-cy="hh-filters-age-to"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <DatePickerFilter
            topLabel={t('Registration Date')}
            placeholder={t('From')}
            onChange={(date) =>
              handleStateFilterChange('registrationDateFrom', date)
            }
            value={filter.registrationDateFrom}
            dataCy="ind-filters-reg-date-from"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <DatePickerFilter
            placeholder={t('To')}
            onChange={(date) =>
              handleStateFilterChange('registrationDateTo', date)
            }
            value={filter.registrationDateTo}
            dataCy="ind-filters-reg-date-to"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) =>
              handleStateFilterChange('hasGrievanceTicket', e.target.value)
            }
            label={t('Has a Grievance Ticket')}
            value={filter.hasGrievanceTicket}
            data-cy="ind-filters-grievance-ticket"
          >
            {YES_NO_CHOICES.map((choice) => (
              <MenuItem key={choice.value} value={choice.value}>
                {t(choice.label)}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <AdminAreaAutocompleteMultipleRestFilter
            value={filter.admin1 || []}
            onChange={(_, option) => {
              handleStateFilterChange('admin1', option);
            }}
            level={1}
            dataCy="filter-admin1"
            disabled={filter.admin2?.length > 0}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <AdminAreaAutocompleteMultipleRestFilter
            value={filter.admin2 || []}
            onChange={(_, option) => {
              handleStateFilterChange('admin2', option);
            }}
            level={2}
            dataCy="filter-admin2"
            disabled={filter.admin1?.length > 0}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <SelectFilter
            onChange={(e) =>
              handleStateFilterChange('receivedAssistance', e.target.value)
            }
            label={t('Received Assistance')}
            value={filter.receivedAssistance}
            data-cy="ind-filters-received-assistance"
          >
            {YES_NO_CHOICES.map((choice) => (
              <MenuItem key={choice.value} value={choice.value}>
                {t(choice.label)}
              </MenuItem>
            ))}
          </SelectFilter>
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </FiltersSection>
  );
};
