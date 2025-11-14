// Helper to check if search contains a keyword
const searchIncludes = (search: unknown, keyword: string) =>
  typeof search === 'string' && search.includes(keyword);
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
import {
  GRIEVANCE_CATEGORIES_NAMES,
  GRIEVANCE_ISSUE_TYPES_NAMES,
  GRIEVANCE_TICKET_STATES,
  GRIEVANCE_TICKET_STATES_NAMES,
} from '@utils/constants';
import { getGrievanceDetailsPath } from '@components/grievances/utils/createGrievanceUtils';

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

  const grvQueryVariables = {
    businessAreaSlug: businessArea,
    program: programId,
    search:
      typeof appliedFilter.search === 'string'
        ? appliedFilter.search.trim()
        : '',
  };

  // Households query
  const {
    data: hhData,
    isLoading: isLoadingHouseholds,
    error: errorHouseholds,
  } = useQuery<PaginatedHouseholdListList>({
    queryKey: [
      'businessAreasHouseholdsList',
      hhQueryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasHouseholdsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          hhQueryVariables,
          { withPagination: true },
        ),
      ),
    enabled: searchIncludes(appliedFilter.search, 'HH'),
  });

  // Individuals query
  const {
    data: indData,
    isLoading: isLoadingIndividuals,
    error: errorIndividuals,
  } = useQuery<PaginatedIndividualListList>({
    queryKey: [
      'businessAreasIndividualsList',
      indQueryVariables,
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasIndividualsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          indQueryVariables,
          { withPagination: true },
        ),
      ),
    enabled: searchIncludes(appliedFilter.search, 'IND'),
  });

  // Grievances query (if needed)
  const {
    data: grvData,
    isLoading: isLoadingGrievances,
    error: errorGrievances,
  } = useQuery({
    queryKey: [
      'businessAreasGrievancesList',
      grvQueryVariables,
      businessArea,
      programId,
      appliedFilter.search,
    ],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsList({
        businessAreaSlug: businessArea,
        search:
          typeof appliedFilter.search === 'string'
            ? appliedFilter.search.trim()
            : '',
        limit: 50,
        offset: 0,
      }),
    enabled: searchIncludes(appliedFilter.search, 'GRV'),
  });

  // Debug logs
  console.log('hhData', hhData);
  console.log('indData', indData);
  console.log('grvData', grvData);

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
          {isLoadingHouseholds && <div>{t('Loading households...')}</div>}
          {errorHouseholds && <div>{t('Error loading households')}</div>}
          {isLoadingIndividuals && <div>{t('Loading individuals...')}</div>}
          {errorIndividuals && <div>{t('Error loading individuals')}</div>}
          {isLoadingGrievances && <div>{t('Loading grievances...')}</div>}
          {errorGrievances && <div>{t('Error loading grievances')}</div>}
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
                    <TableCell>{t('Full Name')}</TableCell>
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
                          <TableCell>{individual.fullName}</TableCell>
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

          {grvData && (
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t('Unicef ID')}</TableCell>
                    <TableCell>{t('Status')}</TableCell>
                    <TableCell>{t('Category')}</TableCell>
                    <TableCell>{t('Issue Type')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {grvData.results && grvData.results.length > 0 ? (
                    grvData.results.map((grv) => {
                      const grvDetailsPath = getGrievanceDetailsPath(
                        grv.id,
                        grv.category,
                        baseUrl,
                      );
                      return (
                        <TableRow key={grv.id} hover>
                          <TableCell>
                            <BlackLink to={grvDetailsPath}>
                              {grv.unicefId}
                            </BlackLink>
                          </TableCell>
                          <TableCell>
                            {GRIEVANCE_TICKET_STATES_NAMES[grv.status]}
                          </TableCell>
                          <TableCell>
                            {GRIEVANCE_CATEGORIES_NAMES[grv.category]}
                          </TableCell>
                          <TableCell>
                            {GRIEVANCE_ISSUE_TYPES_NAMES[grv.issueType]}
                          </TableCell>
                        </TableRow>
                      );
                    })
                  ) : (
                    <TableRow>
                      <TableCell colSpan={3}>{t('No results found')}</TableCell>
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
