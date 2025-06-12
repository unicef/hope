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
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { IndividualsListTable } from '../../tables/population/IndividualsListTable';

export const HouseholdMembersPage = (): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { programHasPdu, selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

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

  const [currentTab, setCurrentTab] = useState(
    isNewTemplateJustCreated ? 1 : 0,
  );

  const canViewPDUListAndDetails = hasPermissions(
    PERMISSIONS.PDU_VIEW_LIST_AND_DETAILS,
    permissions,
  );

  const canViewHouseholdMembersPage = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST,
    permissions,
  );

  if (householdChoicesLoading || individualChoicesLoading)
    return <LoadingComponent />;

  if (!individualChoicesData || !householdChoicesData || permissions === null)
    return null;

  if (!canViewHouseholdMembersPage) return <PermissionDenied />;

  return (
    <>
      <PageHeader
        title={beneficiaryGroup?.memberLabelPlural}
        tabs={
          <Tabs
            value={currentTab}
            onChange={(_, newValue) => {
              setCurrentTab(newValue);
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
                  choicesData={householdChoicesData}
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
