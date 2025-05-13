import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useIndividualChoiceDataQuery } from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { PeriodicDataUpdates } from '@components/periodicDataUpdates/PeriodicDataUpdates'; // Import PeriodicDataUpdates component
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { PeopleListTable } from '@containers/tables/people/PeopleListTable';
import { PeopleFilter } from '@components/people/PeopleFilter';
import { Box, Tabs, Tab, Fade, Tooltip } from '@mui/material';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export const PeoplePage = (): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { programHasPdu } = useProgramContext();
  const { businessArea } = useBaseUrl();
  const isNewTemplateJustCreated =
    location.state?.isNewTemplateJustCreated || false;
  const permissions = usePermissions();

  const { data: householdChoicesData, isLoading: householdChoicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
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

  const [currentTab, setCurrentTab] = useState(
    isNewTemplateJustCreated ? 1 : 0,
  );

  const { data: individualChoicesData, loading: individualChoicesLoading } =
    useIndividualChoiceDataQuery();

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
              setCurrentTab(newValue);
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
