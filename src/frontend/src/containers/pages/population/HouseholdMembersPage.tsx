import { Box, Fade, Tooltip } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import {
  useHouseholdChoiceDataQuery,
  useIndividualChoiceDataQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { IndividualsFilter } from '@components/population/IndividualsFilter';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { IndividualsListTable } from '../../tables/population/IndividualsListTable';
import { Tabs, Tab } from '@core/Tabs';
import { PeriodicDataUpdates } from '@components/periodicDataUpdates/PeriodicDataUpdates';
import { useProgramContext } from 'src/programContext';

export const HouseholdMembersPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { programHasPdu } = useProgramContext();
  const { businessArea } = useBaseUrl();
  const isNewTemplateJustCreated =
    location.state?.isNewTemplateJustCreated || false;

  const permissions = usePermissions();
  const { data: householdChoicesData, loading: householdChoicesLoading } =
    useHouseholdChoiceDataQuery();

  const { data: individualChoicesData, loading: individualChoicesLoading } =
    useIndividualChoiceDataQuery();

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
        title={t('Household Members')}
        tabs={
          <Tabs
            value={currentTab}
            onChange={(_, newValue) => {
              setCurrentTab(newValue);
            }}
          >
            <Tab data-cy="tab-individuals" label="Individuals" />
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
