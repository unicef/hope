import { DatePickerFilter } from '@core/DatePickerFilter';
import { DocumentSearchField } from '@core/DocumentSearchField';
import { FiltersSection } from '@core/FiltersSection';
import { NumberTextField } from '@core/NumberTextField';
import { SearchTextField } from '@core/SearchTextField';
import { SelectFilter } from '@core/SelectFilter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import Grid from '@mui/material/Grid';
import { MenuItem } from '@mui/material';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { AdminAreaAutocomplete } from '@shared/autocompletes/AdminAreaAutocomplete';
import { LanguageAutocompleteRestFilter } from '@shared/autocompletes/LanguageAutocompleteRestFilter';
import { ProgramAutocompleteRestFilter } from '@shared/autocompletes/ProgramAutocompleteRestFilter';
import { createHandleApplyFilterChange } from '@utils/utils';
import { ReactElement, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

interface NaTicketsFiltersProps {
  filter;
  choicesData: GrievanceChoices;
  setFilter: (filter) => void;
  initialFilter;
  appliedFilter;
  setAppliedFilter: (filter) => void;
}

export const NaTicketsFilters = ({
  filter,
  choicesData,
  setFilter,
  initialFilter,
  appliedFilter,
  setAppliedFilter,
}: NaTicketsFiltersProps): ReactElement => {
  const { t } = useTranslation();
  const { isAllPrograms } = useBaseUrl();
  const navigate = useNavigate();
  const location = useLocation();

  const { handleFilterChange, applyFilterChanges, clearFilter } =
    createHandleApplyFilterChange(
      initialFilter,
      navigate,
      location,
      filter,
      setFilter,
      appliedFilter,
      setAppliedFilter,
    );
  const handleApplyFilter = (): void => {
    applyFilterChanges();
  };

  const handleClearFilter = (): void => {
    clearFilter();
  };

  const updatedPriorityChoices = useMemo(() => {
    const priorityChoices = choicesData.grievanceTicketPriorityChoices;
    return priorityChoices.map((item) => {
      if (item.value === 0) {
        return { ...item, value: 'Not Set' };
      }
      return item;
    });
  }, [choicesData.grievanceTicketPriorityChoices]);

  const updatedUrgencyChoices = useMemo(() => {
    const urgencyChoices = choicesData.grievanceTicketUrgencyChoices;
    return urgencyChoices
      .map((item) => {
        if (item.value === 0) {
          return { ...item, value: 'Not Set' };
        }
        return item;
      })
      .reverse();
  }, [choicesData.grievanceTicketUrgencyChoices]);

  return (
    <FiltersSection
      clearHandler={handleClearFilter}
      applyHandler={handleApplyFilter}
    >
      <Grid container alignItems="flex-end" spacing={3}>
        <Grid size={{ xs: 3 }}>
          <SearchTextField
            value={filter.search}
            label="Search"
            onChange={(e) => handleFilterChange('search', e.target.value)}
            data-cy="filters-search"
            borderRadius="4px 0px 0px 4px"
          />
        </Grid>
        <DocumentSearchField
          onChange={handleFilterChange}
          type={filter.documentType}
          number={filter.documentNumber}
          choices={choicesData?.documentTypeChoices}
        />
        {isAllPrograms && (
          <Grid size={{ xs: 3 }}>
            <ProgramAutocompleteRestFilter
              filter={filter}
              name="program"
              value={filter.program}
              status={[ProgramStatusEnum.ACTIVE]}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          </Grid>
        )}
        <Grid size={{ xs: 2 }}>
          <DatePickerFilter
            topLabel={t('Creation Date')}
            placeholder="From"
            onChange={(date) => handleFilterChange('createdAtBefore', date)}
            value={filter.createdAtBefore}
            fullWidth
            dataCy="filters-creation-date-from"
          />
        </Grid>
        <Grid size={{ xs: 2 }}>
          <DatePickerFilter
            placeholder="To"
            onChange={(date) => handleFilterChange('createdAtAfter', date)}
            value={filter.createdAtAfter}
            fullWidth
            dataCy="filters-creation-date-to"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            topLabel={t('Similarity Score')}
            value={filter.scoreMin}
            placeholder="From"
            onChange={(e) => handleFilterChange('scoreMin', e.target.value)}
            data-cy="filters-similarity-score-from"
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <NumberTextField
            value={filter.scoreMax}
            placeholder="To"
            onChange={(e) => handleFilterChange('scoreMax', e.target.value)}
            data-cy="filters-similarity-score-to"
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LanguageAutocompleteRestFilter
            filter={filter}
            name="preferredLanguage"
            value={filter.preferredLanguage}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            setFilter={setFilter}
            dataCy="filters-preferred-language"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('priority', e.target.value)}
            label={t('Priority')}
            value={filter.priority}
            data-cy="filters-priority"
            fullWidth
          >
            {updatedPriorityChoices?.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 2 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('urgency', e.target.value)}
            label={t('Urgency')}
            value={filter.urgency}
            data-cy="filters-urgency"
            fullWidth
          >
            {updatedUrgencyChoices?.map((item) => (
              <MenuItem key={item.value} value={item.value}>
                {item.name}
              </MenuItem>
            ))}
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 2 }}>
          <SelectFilter
            onChange={(e) => handleFilterChange('areaScope', e.target.value)}
            label={t('Ticket Type')}
            value={filter.areaScope}
            fullWidth
            disableClearable
            data-cy="filters-area-scope"
          >
            <MenuItem value="cross-area">{t('Cross-Area Tickets')}</MenuItem>
            <MenuItem value="all">{t('All Tickets')}</MenuItem>
          </SelectFilter>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <AdminAreaAutocomplete
            level={1}
            filter={filter}
            name="admin1"
            value={filter.admin1}
            disabled={filter.admin2}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filters-admin-level-1"
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <AdminAreaAutocomplete
            level={2}
            filter={filter}
            name="admin2"
            value={filter.admin2}
            disabled={filter.admin1}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={setAppliedFilter}
            dataCy="filters-admin-level-2"
          />
        </Grid>
      </Grid>
    </FiltersSection>
  );
};
