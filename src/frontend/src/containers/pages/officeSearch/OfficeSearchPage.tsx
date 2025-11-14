import { PageHeader } from '@components/core/PageHeader';
import {
  Box,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ReactElement, useState } from 'react';
import { FiltersSection } from '@core/FiltersSection';
import { SearchTextField } from '@core/SearchTextField';
import {
  createHandleApplyFilterChange,
  getFilterFromQueryParams,
} from '@utils/utils';
import { useNavigate, useLocation } from 'react-router-dom';
import { BaseSection } from '@components/core/BaseSection';
import { RestService } from '@restgenerated/index';
import { BlackLink } from '@components/core/BlackLink';
import { PaginatedHouseholdListList } from '@restgenerated/models/PaginatedHouseholdListList';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';

const OfficeSearchPage = (): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { businessArea, programId, baseUrl } = useBaseUrl();

  const initialFilter = {
    search: '',
  };
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

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

  const hhQueryVariables = {
    businessAreaSlug: businessArea,
    programSlug: programId,
    search:
      typeof appliedFilter.search === 'string'
        ? appliedFilter.search.trim()
        : '',
  };

  const indQueryVariables = {
    businessAreaSlug: businessArea,
    programSlug: programId,
    search:
      typeof appliedFilter.search === 'string'
        ? appliedFilter.search.trim()
        : '',
  };

  const {
    data: hhData,
    isLoading,
    error,
  } = useQuery<PaginatedHouseholdListList>({
    queryKey: [
      'businessAreasProgramsHouseholdsList',
      hhQueryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          hhQueryVariables,
          { withPagination: true },
        ),
      ),
    enabled:
      typeof appliedFilter.search === 'string' &&
      appliedFilter.search.includes('HH'),
  });

  const { data: indData } = useQuery<PaginatedIndividualListList>({
    queryKey: [
      'businessAreasProgramsIndividualsList',
      indQueryVariables,
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          indQueryVariables,
          { withPagination: true },
        ),
      ),
    enabled:
      typeof appliedFilter.search === 'string' &&
      appliedFilter.search.includes('IND'),
  });

  console.log('hhData', hhData);
  console.log('indData', indData);

  return (
    <>
      <PageHeader title={t('Office Search')} />
      <Box
        display="flex"
        flexDirection="column"
        data-cy="page-details-container"
      >
        <FiltersSection
          clearHandler={handleClearFilter}
          applyHandler={handleApplyFilter}
        >
          <Grid container alignItems="flex-end" spacing={3}>
            <Grid size={{ xs: 8 }}>
              <SearchTextField
                label={t('Search')}
                value={filter.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                data-cy="office-filters-search"
              />
            </Grid>
          </Grid>
        </FiltersSection>
        <BaseSection>
          {isLoading && <div>{t('Loading...')}</div>}
          {error && <div>{t('Error loading households')}</div>}
          {hhData && (
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t('Unicef ID')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {hhData.results && hhData.results.length > 0 ? (
                    hhData.results.map((household) => {
                      const householdDetailsPath = `/${baseUrl}/population/household/${household.id}`;
                      return (
                        <TableRow key={household.id} hover>
                          <TableCell>
                            <BlackLink to={householdDetailsPath}>
                              {household.unicefId}
                            </BlackLink>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  ) : (
                    <TableRow>
                      <TableCell colSpan={1}>{t('No results found')}</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
          {indData && (
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t('Unicef ID')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {indData.results && indData.results.length > 0 ? (
                    indData.results.map((individual) => {
                      const individualDetailsPath = `/${baseUrl}/population/individuals/${individual.id}`;
                      return (
                        <TableRow key={individual.id} hover>
                          <TableCell>
                            <BlackLink to={individualDetailsPath}>
                              {individual.unicefId}
                            </BlackLink>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  ) : (
                    <TableRow>
                      <TableCell colSpan={1}>{t('No results found')}</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </BaseSection>
      </Box>
    </>
  );
};

export default withErrorBoundary(OfficeSearchPage, 'OfficeSearchPage');
