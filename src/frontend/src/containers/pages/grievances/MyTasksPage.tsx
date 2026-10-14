import type { ReactElement } from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Badge, Button } from '@mui/material';
import DoneAllIcon from '@mui/icons-material/DoneAll';
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
import type { MyTasksTab } from '@restgenerated/models/MyTasksTab';
import { restQueryKey } from '@utils/queryKeys';
import { GrievanceStatuses } from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import { theme } from 'src/theme';
import { useTranslation } from 'react-i18next';
import {
  GRIEVANCES_APPROVE_PERMISSIONS,
  GRIEVANCES_VIEW_LIST_NON_SENSITIVE_PERMISSIONS,
  GRIEVANCES_VIEW_LIST_PERMISSIONS,
  GRIEVANCES_VIEW_LIST_SENSITIVE_PERMISSIONS,
  PERMISSIONS,
  hasPermissions,
} from '../../../config/permissions';

// The tab values travel in the URL as ?tab= and are what the daily digest emails deep-link to;
// they are also sent as my_tasks_tab, so they must stay in step with hope.apps.grievance.constants
// (PRESET_*). Sensitivity is not a tab: every email counts sensitive and other tickets separately
// and links each count with ?sensitive=, which lands on the filter below.
// A tab lists groups of alternatives and needs a match in every one of them: loading any tab
// calls the ticket list, which refuses a user holding no list-view grant of its own.
export const MY_TASKS_TABS = [
  {
    value: 'needs-assignment',
    label: 'NEEDS ASSIGNMENT',
    permissions: [
      GRIEVANCES_VIEW_LIST_PERMISSIONS,
      [PERMISSIONS.GRIEVANCE_ASSIGN],
    ],
  },
  {
    value: 'mine',
    label: 'ASSIGNED TO ME',
    permissions: [GRIEVANCES_VIEW_LIST_PERMISSIONS],
  },
  {
    value: 'pending-approval',
    label: 'PENDING APPROVAL',
    permissions: [
      GRIEVANCES_VIEW_LIST_PERMISSIONS,
      GRIEVANCES_APPROVE_PERMISSIONS,
    ],
  },
];

// Both tabs only ever list active tickets (unassigned ones, and ones waiting for approval), so
// neither offers the ticket-status choice.
const ACTIVE_ONLY_TABS = ['needs-assignment', 'pending-approval'];

export const MY_TASKS_PERMISSIONS = MY_TASKS_TABS.flatMap((tab) =>
  tab.permissions.flat(),
);

// The entry point on the ticket list uses this too, so the button and the page never disagree.
export const availableMyTasksTabs = (
  permissions: string[] | null,
): typeof MY_TASKS_TABS =>
  MY_TASKS_TABS.filter((tab) =>
    tab.permissions.every((group) => hasPermissions(group, permissions)),
  );

export const MyTasksPage = (): ReactElement => {
  const [shouldScroll, setShouldScroll] = useState(false);
  const { businessAreaSlug } = useBaseUrl();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const permissions = usePermissions();
  const location = useLocation();
  const navigate = useNavigate();

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: restQueryKey(RestService.restChoicesGrievanceTicketsRetrieve),
    queryFn: () => RestService.restChoicesGrievanceTicketsRetrieve(),
  });

  const availableTabs = useMemo(
    () => availableMyTasksTabs(permissions),
    [permissions],
  );

  // A POST, but read through useQuery so it reruns on every visit, including the return from a
  // ticket, and so mark-read can drop its answer into the same cache entry.
  const visitQueryKey = restQueryKey(
    RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate,
    { businessAreaSlug },
  );
  const { data: visitData, refetch: refetchVisit } = useQuery({
    queryKey: visitQueryKey,
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate({
        businessAreaSlug,
      }),
    staleTime: 0,
    refetchOnMount: 'always',
    // The visit needs a list-view grant; a user with no tab would get a 403 here and be sent
    // to the access-denied page instead of seeing the Permission Denied message below.
    enabled: availableTabs.length > 0,
  });
  const unreadTabs = visitData?.unreadTabs ?? [];

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
    unread: '',
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

  // The backend scopes the list to the tab and marks the unread rows. Sensitivity and unread are
  // filters, so they travel in appliedFilter; only a permission-pinned sensitivity is forced here.
  const extraQueryParams = useMemo(
    () => ({
      myTasksTab: activeTab,
      // Every unassigned closed ticket is unassigned for good, so the tab that exists to get
      // tickets assigned never shows them - matching the count the email was built from.
      ...(activeTab === 'needs-assignment'
        ? { grievanceStatus: GrievanceStatuses.Active }
        : {}),
      ...(pinnedSensitive ? { sensitive: pinnedSensitive } : {}),
      // Left out when unchecked: unread=false would list only the read tickets.
      ...(appliedFilter.unread ? { unread: true } : {}),
    }),
    [activeTab, pinnedSensitive, appliedFilter.unread],
  );

  const { mutate: markTabRead, isPending: markingRead } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasGrievanceTicketsMyTasksMarkReadCreate({
        businessAreaSlug,
        formData: { tab: activeTab as MyTasksTab['tab'] },
      }),
    onSuccess: (data) => {
      queryClient.setQueryData(visitQueryKey, data);
      [
        RestService.restBusinessAreasGrievanceTicketsList,
        RestService.restBusinessAreasGrievanceTicketsCountRetrieve,
        RestService.restBusinessAreasProgramsGrievanceTicketsList,
        RestService.restBusinessAreasProgramsGrievanceTicketsCountRetrieve,
      ].forEach((method) =>
        queryClient.invalidateQueries({ queryKey: restQueryKey(method) }),
      );
    },
  });

  const handleTabChange = (newTab: string): void => {
    // A preset change makes the previous category selection meaningless, as on the ticket list,
    // and the needs-assignment tab has no ticket-status choice to carry over.
    const reset = {
      category: '',
      issueType: '',
      program: '',
      ...(ACTIVE_ONLY_TABS.includes(newTab)
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
    // The dots are only fetched on mount otherwise, so a colleague's change made while the page
    // was open would not show on the tab being switched to.
    refetchVisit();
  };

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null || permissions.length === 0)
    return <LoadingComponent />;
  if (!availableTabs.length)
    return <PermissionDenied permission={MY_TASKS_PERMISSIONS} />;
  if (!choicesData) return null;

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
        <Tab
          data-cy={`tab-${tab.value}`}
          key={tab.value}
          label={
            <Badge
              variant="dot"
              invisible={!unreadTabs.includes(tab.value)}
              data-cy={
                unreadTabs.includes(tab.value)
                  ? `tab-unread-dot-${tab.value}`
                  : undefined
              }
              sx={{
                '& .MuiBadge-badge': {
                  backgroundColor: theme.hctPalette.lightBlue,
                  right: -8,
                },
              }}
            >
              {tab.label}
            </Badge>
          }
        />
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
        showStatusFilter={!ACTIVE_ONLY_TABS.includes(activeTab)}
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
          refetchOnMount="always"
          toolbarActions={
            <Button
              variant="outlined"
              color="primary"
              startIcon={<DoneAllIcon />}
              disabled={!unreadTabs.includes(activeTab) || markingRead}
              onClick={() => markTabRead()}
              data-cy="button-mark-all-read"
            >
              {t('Mark all as read')}
            </Button>
          }
        />
      </div>
    </>
  );
};

export default withErrorBoundary(MyTasksPage, 'MyTasksPage');
