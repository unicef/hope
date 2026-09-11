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
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';

// The tab values travel in the URL as ?tab= and are what the daily digest emails deep-link to;
// they must stay in step with hope.apps.grievance.constants (PRESET_*).
export const MY_TASKS_TABS = [
  {
    value: 'needs-assignment',
    label: 'NEEDS ASSIGNMENT',
    permissions: [PERMISSIONS.GRIEVANCE_ASSIGN],
  },
  {
    value: 'mine-sensitive',
    label: 'ASSIGNED TO ME - SENSITIVE',
    permissions: [
      PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
    ],
  },
  {
    value: 'mine',
    label: 'ASSIGNED TO ME - OTHER',
    permissions: [
      PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
    ],
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

  // The preset axes are derived from the tab, never from the filter bar, so they stay out of the
  // URL: ?tab= is the single thing an email has to carry.
  const extraQueryParams = useMemo(() => {
    switch (activeTab) {
      case 'needs-assignment':
        return { unassigned: true };
      case 'mine-sensitive':
        return { assignedTo: currentUserId, sensitive: 'true' };
      case 'mine':
        return { assignedTo: currentUserId, sensitive: 'false' };
      default:
        return {};
    }
  }, [activeTab, currentUserId]);

  const handleTabChange = (newTab: string): void => {
    const params = new URLSearchParams(location.search);
    params.set('tab', newTab);
    navigate({ search: params.toString() });
    // A preset change makes the previous category selection meaningless, as on the ticket list.
    const reset = { category: '', issueType: '', program: '' };
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
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={(f) => {
          setAppliedFilter(f);
          setShouldScroll(true);
        }}
      />
      <div ref={tableRef}>
        <GrievancesTable
          filter={appliedFilter}
          columns={MY_TASKS_COLUMNS}
          extraQueryParams={extraQueryParams}
          defaultOrderBy="total_days"
          title="My Tasks"
        />
      </div>
    </>
  );
};

export default withErrorBoundary(MyTasksPage, 'MyTasksPage');
