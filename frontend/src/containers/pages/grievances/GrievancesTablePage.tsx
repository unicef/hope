import { Tab, Tabs } from '@material-ui/core';
import React, { useState } from 'react';
import { useHistory, useLocation, useParams } from 'react-router-dom';
import { useGrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { GrievancesFilters } from '../../../components/grievances/GrievancesTable/GrievancesFilters';
import { GrievancesTable } from '../../../components/grievances/GrievancesTable/GrievancesTable';
import { hasPermissionInModule } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  GRIEVANCE_TICKETS_TYPES,
  GrievanceSearchTypes,
  GrievanceStatuses,
  GrievanceTypes,
} from '../../../utils/constants';
import { getFilterFromQueryParams } from '../../../utils/utils';

export const GrievancesTablePage = (): React.ReactElement => {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { id, cashPlanId } = useParams();
  const location = useLocation();
  const history = useHistory();
  const isUserGenerated = location.pathname.indexOf('user-generated') !== -1;

  const initialFilter = {
    search: '',
    searchType: GrievanceSearchTypes.TicketID,
    status: '',
    fsp: '',
    createdAtRangeMin: undefined,
    createdAtRangeMax: undefined,
    category: '',
    issueType: '',
    assignedTo: '',
    admin: '',
    registrationDataImport: id,
    cashPlan: cashPlanId,
    scoreMin: '',
    scoreMax: '',
    grievanceType: isUserGenerated ? GrievanceTypes[0] : GrievanceTypes[1],
    grievanceStatus: GrievanceStatuses.Active,
    priority: '',
    urgency: '',
    preferredLanguage: '',
  };

  const [selectedTab, setSelectedTab] = useState(
    isUserGenerated
      ? GRIEVANCE_TICKETS_TYPES.userGenerated
      : GRIEVANCE_TICKETS_TYPES.systemGenerated,
  );

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  const grievanceTicketsTypes = ['USER-GENERATED', 'SYSTEM-GENERATED'];
  const userGeneratedPath = `/${businessArea}/grievance-and-feedback/tickets/user-generated`;
  const systemGeneratedPath = `/${businessArea}/grievance-and-feedback/tickets/system-generated`;

  const mappedTabs = grievanceTicketsTypes.map((el) => (
    <Tab key={el} label={el} />
  ));
  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={(event: React.ChangeEvent<{}>, newValue: number) => {
        setSelectedTab(newValue);
        setFilter({
          ...filter,
          grievanceType: GrievanceTypes[newValue],
          category: '',
        });
        history.push(newValue === 0 ? userGeneratedPath : systemGeneratedPath);
      }}
      indicatorColor='primary'
      textColor='primary'
      variant='scrollable'
      scrollButtons='auto'
      aria-label='tabs'
    >
      {mappedTabs}
    </Tabs>
  );

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions))
    return <PermissionDenied />;
  if (!choicesData) return null;

  return (
    <>
      <PageHeader tabs={tabs} title='Grievance Tickets' />
      <GrievancesFilters
        choicesData={choicesData}
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
        selectedTab={selectedTab}
      />
      <GrievancesTable
        filter={appliedFilter}
        businessArea={businessArea}
        selectedTab={selectedTab}
      />
    </>
  );
};
