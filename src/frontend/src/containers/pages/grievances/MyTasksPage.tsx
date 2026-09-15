import type { ReactElement } from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { Tab, Tabs } from '@core/Tabs';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { MyTasksFilters } from '@components/grievances/MyTasks/MyTasksFilters';
import { GrievancesTable } from '@components/grievances/GrievancesTable/GrievancesTable';
import { MY_TASKS_COLUMNS } from '@components/grievances/GrievancesTable/GrievancesTableColumns';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { GrievanceStatuses } from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import {
  GRIEVANCES_VIEW_LIST_NON_SENSITIVE_PERMISSIONS,
  GRIEVANCES_VIEW_LIST_PERMISSIONS,
  GRIEVANCES_VIEW_LIST_SENSITIVE_PERMISSIONS,
  PERMISSIONS,
  hasPermissions,
} from '../../../config/permissions';

// The tab values travel in the URL as ?tab= and are what the daily digest emails deep-link to;
// they must stay in step with hope.apps.grievance.constants (PRESET_*). Sensitivity is not a tab:
// every email counts sensitive and other tickets separately and links each count with ?sensitive=,
// which lands on the filter below.
export const MY_TASKS_TABS = [
  {
    value: 'needs-assignment',
    label: 'NEEDS ASSIGNMENT',
    permissions: [PERMISSIONS.GRIEVANCE_ASSIGN],
  },
  {
    value: 'mine',
    label: 'ASSIGNED TO ME',
    permissions: GRIEVANCES_VIEW_LIST_PERMISSIONS,
  },
];

export const MY_TASKS_PERMISSIONS = MY_TASKS_TABS.flatMap(
  (tab) => tab.permissions,
);

export const MyTasksPage = (): ReactElement => {
  const [shouldScroll, setShouldScroll] = useState(false);
  const { businessAreaSlug, programCode } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();
  const navigate = useNavigate();

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: restQueryKey(RestService.restChoicesGrievanceTicketsRetrieve),
    queryFn: () => RestService.restChoicesGrievanceTicketsRetrieve(),
  });

  // Same param shape as usePermissions and GrievancesTable, so react-query serves one request.
  const currentUserParams = {
    businessAreaSlug,
    program: programCode === 'all' ? undefined : programCode,
  };
  const { data: currentUserData, isLoading: currentUserLoading } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasUsersProfileRetrieve,
      currentUserParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasUsersProfileRetrieve(currentUserParams),
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  const availableTabs = useMemo(
    () =>
      MY_TASKS_TABS.filter((tab) =>
        hasPermissions(tab.permissions, permissions),
      ),
    [permissions],
  );

  const requestedTab = new URLSearchParams(location.search).get('tab');
  const activeTab =
    availableTabs.find((tab) => tab.value === requestedTab)?.value ??
    availableTabs[0]?.value;

  // Always state the tab in the URL, so a bare /my-tasks is shareable and reloads identically.
  useEffect(() => {
    if (!activeTab || requestedTab === activeTab) return;
    const params = new URLSearchParams(location.search);
    params.set('tab', activeTab);
    navigate({ search: params.toString() }, { replace: true });
  }, [activeTab, requestedTab, location.search, navigate]);

  const initialFilter = {
    search: '',
    documentType: '',
    documentNumber: '',
    status: '',
    fsp: '',
    createdAtBefore: '',
    createdAtAfter: '',
    category: '',
    issueType: '',
    assignedTo: '',
    createdBy: '',
    admin1: '',
    admin2: '',
    registrationDataImport: '',
    cashPlan: '',
    scoreMin: '',
    scoreMax: '',
    grievanceType: '',
    grievanceStatus: GrievanceStatuses.Active,
    priority: '',
    urgency: '',
    submissionChannel: '',
    preferredLanguage: '',
    program: '',
    areaScope: 'all',
    overdue: '',
    sensitive: '',
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  const currentUserId = currentUserData?.id;

  // Sensitive and other grievances are separate grants. A user holding only one of them has no
  // choice to make, so the filter is decided for them here and its control is hidden.
  const canSeeSensitive = hasPermissions(
    GRIEVANCES_VIEW_LIST_SENSITIVE_PERMISSIONS,
    permissions,
  );
  const canSeeOther = hasPermissions(
    GRIEVANCES_VIEW_LIST_NON_SENSITIVE_PERMISSIONS,
    permissions,
  );
  const pinnedSensitive =
    canSeeSensitive === canSeeOther ? null : canSeeSensitive ? 'true' : 'false';
  // Folded into the filter, not just into the query, so the category list below reacts to a
  // pinned value exactly as it does to a chosen one.
  const pin = pinnedSensitive ? { sensitive: pinnedSensitive } : {};

  // The tab's own axis is derived from the tab, never from the filter bar, so it stays out of the
  // URL. Sensitivity is the exception: it is a filter, so it travels in appliedFilter, and only a
  // permission-pinned value is forced here.
  const extraQueryParams = useMemo(
    () => ({
      ...(activeTab === 'needs-assignment'
        ? // Every unassigned closed ticket is unassigned for good, so the tab that exists to get
          // tickets assigned never shows them - matching the count the email was built from.
          { unassigned: true, grievanceStatus: GrievanceStatuses.Active }
        : { assignedTo: currentUserId }),
      ...(pinnedSensitive ? { sensitive: pinnedSensitive } : {}),
    }),
    [activeTab, currentUserId, pinnedSensitive],
  );

  const handleTabChange = (newTab: string): void => {
    // A preset change makes the previous category selection meaningless, as on the ticket list,
    // and the needs-assignment tab has no ticket-status choice to carry over.
    const reset = {
      category: '',
      issueType: '',
      program: '',
      ...(newTab === 'needs-assignment'
        ? { grievanceStatus: GrievanceStatuses.Active }
        : {}),
    };
    const params = new URLSearchParams(location.search);
    params.set('tab', newTab);
    // Clear the reset keys from the URL too, or a reload brings the stale selection back.
    Object.keys(reset).forEach((key) => params.delete(key));
    navigate({ search: params.toString() });
    setFilter({ ...filter, ...reset });
    setAppliedFilter({ ...appliedFilter, ...reset });
  };

  if (choicesLoading || currentUserLoading) return <LoadingComponent />;
  if (permissions === null || permissions.length === 0)
    return <LoadingComponent />;
  if (!availableTabs.length)
    return <PermissionDenied permission={MY_TASKS_PERMISSIONS} />;
  if (!choicesData || !currentUserData) return null;

  const tabs = (
    <Tabs
      value={availableTabs.findIndex((tab) => tab.value === activeTab)}
      onChange={(_event, newValue: number) =>
        handleTabChange(availableTabs[newValue].value)
      }
      indicatorColor="primary"
      textColor="primary"
      variant="scrollable"
      scrollButtons="auto"
      aria-label="tabs"
    >
      {availableTabs.map((tab) => (
        <Tab data-cy={`tab-${tab.value}`} key={tab.value} label={tab.label} />
      ))}
    </Tabs>
  );

  return (
    <>
      <PageHeader tabs={tabs} title="My Tasks" />
      <MyTasksFilters
        choicesData={choicesData}
        filter={{ ...filter, ...pin }}
        setFilter={setFilter}
        initialFilter={initialFilter}
        showSensitiveFilter={pinnedSensitive === null}
        showStatusFilter={activeTab !== 'needs-assignment'}
        appliedFilter={appliedFilter}
        setAppliedFilter={(f) => {
          setAppliedFilter(f);
          setShouldScroll(true);
        }}
      />
      <div ref={tableRef}>
        <GrievancesTable
          filter={{ ...appliedFilter, ...pin }}
          columns={MY_TASKS_COLUMNS}
          extraQueryParams={extraQueryParams}
          defaultOrderBy="total_days"
          title="My Tasks"
          // Needs Assignment only ever lists unassigned active tickets, none of which are
          // closable, so the bulk-close action has nothing to do there.
          showBulkClose={activeTab !== 'needs-assignment'}
        />
      </div>
    </>
  );
};

export default withErrorBoundary(MyTasksPage, 'MyTasksPage');
