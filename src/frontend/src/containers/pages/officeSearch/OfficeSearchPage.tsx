import {
  Box,
  Grid,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@mui/material';
import { PageHeader } from '@components/core/PageHeader';
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
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';
import { PermissionDenied } from '@components/core/PermissionDenied';

const OfficeSearchPage = (): ReactElement => {
  const NoResultsMessage = (
    <Box mt={4} textAlign="center">
      <Typography variant="h6">
        No results found. Please adjust your search criteria and try again.
      </Typography>
    </Box>
  );
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const canViewHouseholds = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST,
    permissions,
  );
  const canViewIndividuals = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST,
    permissions,
  );
  const canViewGrievances = hasPermissions(
    PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_LIST,
    permissions,
  );
  const canViewPaymentPlans = hasPermissions(
    PERMISSIONS.PM_VIEW_LIST,
    permissions,
  );
  const canViewPayments = hasPermissions(
    PERMISSIONS.PM_VIEW_PAYMENT_LIST,
    permissions,
  );

  const initialFilter = {
    searchFor: '',
    basedOnId: '',
    officeSearch: '',
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
    officeSearch: appliedFilter.officeSearch,
  };

  const indQueryVariables = {
    businessAreaSlug: businessArea,
    officeSearch: appliedFilter.officeSearch,
  };

  const grvQueryVariables = {
    businessAreaSlug: businessArea,
    officeSearch: appliedFilter.officeSearch,
  };

  const ppQueryVariables = {
    businessAreaSlug: businessArea,
    officeSearch: appliedFilter.officeSearch,
  };

  const paymentsQueryVariables = {
    businessAreaSlug: businessArea,
    officeSearch: appliedFilter.officeSearch,
  };

  // Query variables for Payment Plans and Payments

  // Households query
  const {
    data: hhData,
    isLoading: isLoadingHouseholds,
    error: errorHouseholds,
  } = useQuery<PaginatedHouseholdListList>({
    queryKey: [
      'businessAreasHouseholdsList',
      hhQueryVariables,
      businessArea,
      appliedFilter.officeSearch,
    ],
    queryFn: () =>
      RestService.restBusinessAreasHouseholdsList(
        createApiParams({ businessAreaSlug: businessArea }, hhQueryVariables, {
          withPagination: false,
        }),
      ),
    enabled: appliedFilter.searchFor === 'HH' && !!appliedFilter.officeSearch,
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
      appliedFilter.officeSearch,
    ],
    queryFn: () =>
      RestService.restBusinessAreasIndividualsList(
        createApiParams({ businessAreaSlug: businessArea }, indQueryVariables, {
          withPagination: false,
        }),
      ),
    enabled: appliedFilter.searchFor === 'IND' && !!appliedFilter.officeSearch,
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
      appliedFilter.searchFor,
      appliedFilter.officeSearch,
    ],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsList(
        createApiParams({ businessAreaSlug: businessArea }, grvQueryVariables, {
          withPagination: false,
        }),
      ),
    enabled: appliedFilter.searchFor === 'GRV' && !!appliedFilter.officeSearch,
  });

  // Payment Plans query (for 'PP' search)
  const {
    data: ppData,
    isLoading: isLoadingPaymentPlans,
    error: errorPaymentPlans,
  } = useQuery({
    queryKey: [
      'businessAreasPaymentPlansList',
      ppQueryVariables,
      businessArea,
      appliedFilter.officeSearch,
      appliedFilter.searchFor,
    ],
    queryFn: () =>
      RestService.restBusinessAreasPaymentPlansList(
        createApiParams({ businessAreaSlug: businessArea }, ppQueryVariables, {
          withPagination: false,
        }),
      ),
    enabled: appliedFilter.searchFor === 'PP' && !!appliedFilter.officeSearch,
  });

  // Payments query (for 'RCPT' search)

  const {
    data: paymentsData,
    isLoading: isLoadingPayments,
    error: errorPayments,
  } = useQuery({
    queryKey: [
      'businessAreasPaymentsList',
      paymentsQueryVariables,
      businessArea,
      appliedFilter.officeSearch,
    ],
    queryFn: () =>
      RestService.restBusinessAreasPaymentsList(
        createApiParams(
          { businessAreaSlug: businessArea },
          paymentsQueryVariables,
          {
            withPagination: false,
          },
        ),
      ),
    enabled: appliedFilter.searchFor === 'RCPT' && !!appliedFilter.officeSearch,
  });

  // Filter basedOnId options based on searchFor selection
  const getBasedOnIdOptions = () => {
    const allOptions = [
      canViewHouseholds && {
        value: 'HH',
        label: `${beneficiaryGroup?.groupLabel || 'Household'}`,
      },
      canViewIndividuals && {
        value: 'IND',
        label: `${beneficiaryGroup?.memberLabel || 'Individual'}`,
      },
      canViewGrievances && { value: 'GRV', label: 'Grievance' },
      canViewPaymentPlans && { value: 'PP', label: 'Payment Plan' },
      canViewPayments && { value: 'RCPT', label: 'Payment' },
    ].filter(Boolean);

    // Filter out incompatible combinations
    if (filter.searchFor === 'GRV') {
      return allOptions.filter((option) => option.value !== 'PP');
    }
    if (filter.searchFor === 'PP') {
      return allOptions.filter((option) => option.value !== 'GRV');
    }
    return allOptions;
  };

  const basedOnIdOptions = getBasedOnIdOptions();

  const searchForOptions = [
    canViewHouseholds && {
      value: 'HH',
      label: beneficiaryGroup?.groupLabel || 'Household',
    },
    canViewIndividuals && {
      value: 'IND',
      label: beneficiaryGroup?.memberLabel || 'Individual',
    },
    canViewGrievances && { value: 'GRV', label: 'Grievance' },
    canViewPaymentPlans && { value: 'PP', label: 'Payment Plan' },
    canViewPayments && { value: 'RCPT', label: 'Payment' },
  ].filter(Boolean);

  if (!hasPermissions(PERMISSIONS.SEARCH_BUSINESS_AREAS, permissions)) {
    return <PermissionDenied />;
  }

  return (
    <>
      <PageHeader title={t('Country Search')} />
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
            <Grid size={3}>
              <FormControl fullWidth size="small">
                <InputLabel id="search-for-label">Search For</InputLabel>
                <Select
                  labelId="search-for-label"
                  id="search-for"
                  value={filter.searchFor}
                  label="Search For"
                  onChange={(e) =>
                    handleFilterChange('searchFor', e.target.value)
                  }
                >
                  {searchForOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={3}>
              <FormControl fullWidth size="small">
                <InputLabel id="based-on-id-label">Based on ID</InputLabel>
                <Select
                  labelId="based-on-id-label"
                  id="based-on-id"
                  value={filter.basedOnId}
                  label="Based on ID"
                  onChange={(e) =>
                    handleFilterChange('basedOnId', e.target.value)
                  }
                >
                  {basedOnIdOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={6}>
              <SearchTextField
                label={t('Search Value')}
                value={filter.officeSearch}
                onChange={(e) =>
                  handleFilterChange('officeSearch', e.target.value)
                }
                data-cy="office-filters-search"
              />
            </Grid>
          </Grid>
        </FiltersSection>
        <BaseSection>
          {/* Households */}
          {appliedFilter.searchFor === 'HH' &&
            (isLoadingHouseholds ? (
              <div>{t('Loading households...')}</div>
            ) : errorHouseholds ? (
              <div>{t('Error loading households')}</div>
            ) : hhData?.results?.length ? (
              <HHDataTable hhData={hhData} />
            ) : (
              NoResultsMessage
            ))}
          {/* Individuals */}
          {appliedFilter.searchFor === 'IND' &&
            (isLoadingIndividuals ? (
              <div>{t('Loading individuals...')}</div>
            ) : errorIndividuals ? (
              <div>{t('Error loading individuals')}</div>
            ) : indData?.results?.length ? (
              <INDDataTable indData={indData} />
            ) : (
              NoResultsMessage
            ))}
          {/* Grievances */}
          {appliedFilter.searchFor === 'GRV' &&
            (isLoadingGrievances ? (
              <div>{t('Loading grievances...')}</div>
            ) : errorGrievances ? (
              <div>{t('Error loading grievances')}</div>
            ) : grvData?.results?.length ? (
              <GRVDataTable grvData={grvData} />
            ) : (
              NoResultsMessage
            ))}
          {/* Payment Plans */}
          {appliedFilter.searchFor === 'PP' &&
            (isLoadingPaymentPlans ? (
              <div>{t('Loading payment plans...')}</div>
            ) : errorPaymentPlans ? (
              <div>{t('Error loading payment plans')}</div>
            ) : ppData?.results?.length ? (
              <PPDataTable ppData={ppData} />
            ) : (
              NoResultsMessage
            ))}
          {/* Payments */}
          {appliedFilter.searchFor === 'RCPT' &&
            (isLoadingPayments ? (
              <div>{t('Loading payments...')}</div>
            ) : errorPayments ? (
              <div>{t('Error loading payments')}</div>
            ) : paymentsData?.results?.length ? (
              <PaymentsDataTable paymentsData={paymentsData} />
            ) : (
              NoResultsMessage
            ))}
        </BaseSection>
      </Box>
    </>
  );
};

export default withErrorBoundary(OfficeSearchPage, 'OfficeSearchPage');
