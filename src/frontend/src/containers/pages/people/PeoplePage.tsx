import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PeopleFilter } from '@components/people/PeopleFilter';
import { PeriodicDataUpdates } from '@components/periodicDataUpdates/PeriodicDataUpdates'; // Import PeriodicDataUpdates component
import { PeopleListTable } from '@containers/tables/people/PeopleListTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box, Fade, Tab, Tabs, Tooltip } from '@mui/material';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

const PeoplePage = (): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { programHasPdu = false } = useProgramContext();
  const { businessArea } = useBaseUrl();

  const permissions = usePermissions();
  const { data: householdChoicesData, isLoading: householdChoicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

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
    documentType: householdChoicesData?.documentTypeChoices?.[0].value,
    documentNumber: '',
    admin1: '',
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

  const tabParam = new URLSearchParams(location.search).get('tab');
  const initialTab = tabParam === 'periodic-data-updates' ? 1 : 0;
  const [currentTab, setCurrentTab] = useState(initialTab);

  // Sync tab with URL param on location change
  useEffect(() => {
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

  if (householdChoicesLoading || individualChoicesLoading)
    return <LoadingComponent />;

  if (!individualChoicesData || !householdChoicesData || permissions === null)
    return null;

  if (
    !hasPermissions(PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST, permissions)
  )
    return <PermissionDenied />;

  return (
    <>
      <PageHeader
        title={t('People')}
        tabs={
          <Tabs
            value={currentTab}
            onChange={(_, newValue) => {
              handleTabChange(newValue);
            }}
          >
            <Tab data-cy="tab-individuals" label="Individuals" />
            {!programHasPdu ? (
              <Tooltip
                title={t(
                  'Programme does not have defined fields for periodic updates',
                )}
              >
                <span>
                  <Tab
                    disabled={!programHasPdu}
                    data-cy="tab-periodic-data-updates"
                    label="Periodic Data Updates"
                  />
                </span>
              </Tooltip>
            ) : (
              <Tab
                disabled={!programHasPdu}
                data-cy="tab-periodic-data-updates"
                label="Periodic Data Updates"
              />
            )}
          </Tabs>
        }
      />
      <Fade in={true} timeout={500} key={currentTab}>
        <Box>
          {currentTab === 0 ? (
            <>
              <PeopleFilter
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
                <PeopleListTable
                  filter={appliedFilter}
                  businessArea={businessArea}
                  canViewDetails={hasPermissions(
                    PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
                    permissions,
                  )}
                />
              </Box>
            </>
          ) : (
            <PeriodicDataUpdates />
          )}
        </Box>
      </Fade>
    </>
  );
};

export default withErrorBoundary(PeoplePage, 'PeoplePage');
