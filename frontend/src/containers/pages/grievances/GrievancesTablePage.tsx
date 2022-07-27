import { Tab, Tabs } from '@material-ui/core';
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissionInModule } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { useGrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { GrievancesFilters } from '../../../components/grievances/GrievancesTable/GrievancesFilters';
import { GrievancesTable } from '../../../components/grievances/GrievancesTable/GrievancesTable';
import {
  GrievanceSearchTypes,
  GrievanceStatuses,
  GrievanceTypes,
  GRIEVANCE_TICKETS_TYPES,
} from '../../../utils/constants';

export function GrievancesTablePage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { id, cashPlanId } = useParams();
  const [filter, setFilter] = useState({
    search: '',
    status: '',
    fsp: '',
    createdAtRange: '',
    category: '',
    issueType: '',
    assignedTo: '',
    admin: null,
    registrationDataImport: id,
    cashPlan: cashPlanId,
    scoreMin: null,
    scoreMax: null,
    grievanceType: GrievanceTypes[0],
    grievanceStatus: GrievanceStatuses.Active,
    priority: '',
    urgency: '',
    searchType: GrievanceSearchTypes.TicketID,
  });
  const [selectedTab, setSelectedTab] = useState(
    GRIEVANCE_TICKETS_TYPES.userGenerated,
  );
  const debouncedFilter = useDebounce(filter, 500);
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  const grievanceTicketsTypes = ['USER-GENERATED', 'SYSTEM-GENERATED'];

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
        onFilterChange={setFilter}
      />
      <GrievancesTable
        filter={debouncedFilter}
        businessArea={businessArea}
        selectedTab={selectedTab}
      />
    </>
  );
}
