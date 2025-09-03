import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PeriodicDataUpdates } from '@components/periodicDataUpdates/PeriodicDataUpdates';
import { IndividualsFilter } from '@components/population/IndividualsFilter';
import { Tab, Tabs } from '@core/Tabs';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box, Fade, Tooltip } from '@mui/material';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { IndividualsListTable } from '../../tables/population/IndividualsListTable';

export const HouseholdMembersPage = (): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { programHasPdu, selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { businessArea } = useBaseUrl();
  const isNewTemplateJustCreated =
    location.state?.isNewTemplateJustCreated || false;

  const permissions = usePermissions();

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery<IndividualChoices>({
      queryKey: ['individualChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const initialFilter = {
    search: '',
    documentType: individualChoicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: '',
    admin2: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    flags: [],
    orderBy: 'unicef_id',
    status: '',
    lastRegistrationDateMin: '',
    lastRegistrationDateMax: '',
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  // Tab index: 0 = individuals, 1 = periodic-data-updates
  const tabParam = new URLSearchParams(location.search).get('tab');
  const initialTab = isNewTemplateJustCreated
    ? 1
    : tabParam === 'periodic-data-updates'
      ? 1
      : 0;
  const [currentTab, setCurrentTab] = useState(initialTab);

  useEffect(() => {
    // Sync tab with URL param on location change
    const tabParamEffect = new URLSearchParams(location.search).get('tab');
    if (tabParamEffect === 'periodic-data-updates' && currentTab !== 1) {
      setCurrentTab(1);
    } else if (
      (tabParamEffect === 'individuals' || !tabParamEffect) &&
      currentTab !== 0
    ) {
      setCurrentTab(0);
    }
  }, [location.search, currentTab]);

  const canViewPDUListAndDetails = hasPermissions(
    PERMISSIONS.PDU_VIEW_LIST_AND_DETAILS,
    permissions,
  );

  const canViewHouseholdMembersPage = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST,
    permissions,
  );

  const handleTabChange = (newValue: number): void => {
    setCurrentTab(newValue);
    if (newValue === 0) {
      navigate(
        {
          search: '?tab=individuals',
        },
        { replace: true },
      );
    } else if (newValue === 1) {
      navigate(
        {
          search: '?tab=periodic-data-updates',
        },
        { replace: true },
      );
    }
  };

  if (individualChoicesLoading) return <LoadingComponent />;

  if (!individualChoicesData || permissions === null) return null;

  if (!canViewHouseholdMembersPage) return <PermissionDenied />;

  return (
    <>
      <PageHeader
        title={beneficiaryGroup?.memberLabelPlural}
        tabs={
          <Tabs
            value={currentTab}
            onChange={(_, newValue) => {
              handleTabChange(newValue);
            }}
          >
            <Tab
              data-cy="tab-individuals"
              label={beneficiaryGroup?.memberLabelPlural}
            />
            {programHasPdu ? (
              canViewPDUListAndDetails ? (
                <Tab
                  data-cy="tab-periodic-data-updates"
                  label="Periodic Data Updates"
                />
              ) : (
                <Tooltip title={t('Permission Denied')}>
                  <span>
                    <Tab
                      disabled
                      data-cy="tab-periodic-data-updates"
                      label="Periodic Data Updates"
                    />
                  </span>
                </Tooltip>
              )
            ) : (
              <Tooltip
                title={t(
                  'Programme does not have defined fields for periodic updates',
                )}
              >
                <span>
                  <Tab
                    disabled
                    data-cy="tab-periodic-data-updates"
                    label="Periodic Data Updates"
                  />
                </span>
              </Tooltip>
            )}
          </Tabs>
        }
      />
      <Fade in={true} timeout={500} key={currentTab}>
        <Box>
          {currentTab === 0 ? (
            <>
              <IndividualsFilter
                filter={filter}
                choicesData={individualChoicesData}
                setFilter={setFilter}
                initialFilter={initialFilter}
                appliedFilter={appliedFilter}
                setAppliedFilter={setAppliedFilter}
              />
              <Box
                display="flex"
                flexDirection="column"
                data-cy="page-details-container"
              >
                <IndividualsListTable
                  filter={appliedFilter}
                  businessArea={businessArea}
                  choicesData={individualChoicesData}
                  canViewDetails={hasPermissions(
                    PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
                    permissions,
                  )}
                />
              </Box>
            </>
          ) : canViewPDUListAndDetails ? (
            <PeriodicDataUpdates />
          ) : (
            <PermissionDenied />
          )}
        </Box>
      </Fade>
    </>
  );
};
export default withErrorBoundary(HouseholdMembersPage, 'HouseholdMembersPage');
