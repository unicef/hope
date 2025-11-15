import { PageHeader } from '@components/core/PageHeader';
import { Box, Grid } from '@mui/material';
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
import { PaginatedHouseholdListList } from '@restgenerated/models/PaginatedHouseholdListList';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';
import HHDataTable from '@containers/pages/officeSearch/HHdataTable';
import INDDataTable from '@containers/pages/officeSearch/INDdataTable';
import GRVDataTable from '@containers/pages/officeSearch/GRVdataTable';
import PPDataTable from '@containers/pages/officeSearch/PPdataTable';
import PaymentsDataTable from '@containers/pages/officeSearch/PaymentsDataTable';

const searchIncludes = (search: unknown, keyword: string) =>
  typeof search === 'string' && search.includes(keyword);

const OfficeSearchPage = (): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { businessArea, programId } = useBaseUrl();

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
        limit: 10,
        offset: 0,
      }),
    enabled: searchIncludes(appliedFilter.search, 'GRV'),
  });

  // Payment Plans query (for 'PP' search)
  const {
    data: ppData,
    isLoading: isLoadingPaymentPlans,
    error: errorPaymentPlans,
  } = useQuery({
    queryKey: [
      'businessAreasProgramsPaymentPlansList',
      businessArea,
      programId,
      appliedFilter.search,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansList({
        businessAreaSlug: businessArea,
        programSlug: programId,
        search:
          typeof appliedFilter.search === 'string'
            ? appliedFilter.search.trim()
            : '',
        limit: 10,
        offset: 0,
      }),
    enabled: searchIncludes(appliedFilter.search, 'PP'),
  });

  // Payments query (for 'RCPT' search)
  const {
    data: paymentsData,
    isLoading: isLoadingPayments,
    error: errorPayments,
  } = useQuery({
    queryKey: ['businessAreasPaymentsList', businessArea, appliedFilter.search],
    queryFn: () =>
      RestService.restBusinessAreasPaymentsList({
        businessAreaSlug: businessArea,
        limit: 10,
        offset: 0,
      }),
    enabled: searchIncludes(appliedFilter.search, 'RCPT'),
  });

  // Debug logs
  console.log('hhData', hhData);
  console.log('indData', indData);
  console.log('grvData', grvData);
  console.log('ppData', ppData);
  console.log('paymentsData', paymentsData);
  //need BA and programSlug, to fetch PP
  //need paymentPlanPk, BA, program, to fetch payments,
  // console.log('paymentsData', paymentsData);

  const nothingToDisplay =
    !hhData?.results?.length &&
    !indData?.results?.length &&
    !grvData?.results?.length &&
    !ppData?.results?.length &&
    !paymentsData?.results?.length;

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
          {isLoadingPaymentPlans && <div>{t('Loading payment plans...')}</div>}
          {errorPaymentPlans && <div>{t('Error loading payment plans')}</div>}
          {isLoadingPayments && <div>{t('Loading payments...')}</div>}
          {errorPayments && <div>{t('Error loading payments')}</div>}
          {hhData && <HHDataTable hhData={hhData} />}
          {indData && <INDDataTable indData={indData} />}
          {grvData && <GRVDataTable grvData={grvData} />}
          {paymentsData && <PaymentsDataTable paymentsData={paymentsData} />}
          {ppData && <PPDataTable ppData={ppData} />}
          {nothingToDisplay && (
            <Box mt={4} textAlign="center">
              <h2>
                Search for Individuals, Households, Grievances, Payment Plans,
                Payments
              </h2>
            </Box>
          )}
        </BaseSection>
      </Box>
    </>
  );
};

export default withErrorBoundary(OfficeSearchPage, 'OfficeSearchPage');
