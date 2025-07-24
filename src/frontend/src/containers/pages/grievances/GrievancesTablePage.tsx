import { ReactElement, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { GrievancesFilters } from '@components/grievances/GrievancesTable/GrievancesFilters';
import { GrievancesTable } from '@components/grievances/GrievancesTable/GrievancesTable';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import {
  GRIEVANCE_TICKETS_TYPES,
  GrievanceStatuses,
  GrievanceTypes,
} from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import { Tabs, Tab } from '@core/Tabs';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { t } from 'i18next';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export const GrievancesTablePage = (): ReactElement => {
  const { businessArea, baseUrl } = useBaseUrl();
  const { isActiveProgram } = useProgramContext();
  const permissions = usePermissions();
  const { id, cashPlanId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  const isUserGenerated = location.pathname.indexOf('user-generated') !== -1;

  const initialFilter = {
    search: '',
    documentType: choicesData?.documentTypeChoices?.[0]?.value,
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
    registrationDataImport: id || '',
    cashPlan: cashPlanId,
    scoreMin: '',
    scoreMax: '',
    grievanceType: isUserGenerated ? 'user' : 'system',
    grievanceStatus: GrievanceStatuses.Active,
    priority: '',
    urgency: '',
    preferredLanguage: '',
    program: '',
    programState: 'all',
    areaScope: 'all',
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

  const grievanceTicketsTypes = ['USER-GENERATED', 'SYSTEM-GENERATED'];
  const userGeneratedPath = `/${baseUrl}/grievance/tickets/user-generated`;
  const systemGeneratedPath = `/${baseUrl}/grievance/tickets/system-generated`;

  const mappedTabs = grievanceTicketsTypes.map((el) => (
    <Tab data-cy={`tab-${el}`} key={el} label={el} />
  ));
  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={(_event, newValue: number) => {
        setSelectedTab(newValue);
        setFilter({
          ...filter,
          grievanceType: GrievanceTypes[newValue],
          category: '',
          program: '',
        });
        setAppliedFilter({
          ...appliedFilter,
          grievanceType: GrievanceTypes[newValue],
          category: '',
          program: '',
        });
        navigate(newValue === 0 ? userGeneratedPath : systemGeneratedPath);
      }}
      indicatorColor="primary"
      textColor="primary"
      variant="scrollable"
      scrollButtons="auto"
      aria-label="tabs"
    >
      {mappedTabs}
    </Tabs>
  );

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null || permissions.length === 0)
    return <LoadingComponent />;

  // Define the permission criteria for viewing grievances
  const hasGrievancesViewPermission = permissions.some(
    (perm) =>
      perm.includes('GRIEVANCES_VIEW_LIST') ||
      perm.includes('GRIEVANCES_VIEW_DETAILS'),
  );

  if (!hasGrievancesViewPermission) return <PermissionDenied />;
  if (!choicesData) return null;

  return (
    <>
      <PageHeader tabs={tabs} title="Grievance Tickets">
        {hasPermissions(PERMISSIONS.GRIEVANCES_CREATE, permissions) && (
          <ButtonTooltip
            variant="contained"
            color="primary"
            component={Link}
            title={t(
              'Programme has to be active to create a new Grievance Ticket',
            )}
            to={`/${baseUrl}/grievance/new-ticket`}
            data-cy="button-new-ticket"
            disabled={!isActiveProgram}
          >
            {t('NEW TICKET')}
          </ButtonTooltip>
        )}
      </PageHeader>
      <GrievancesFilters
        choicesData={choicesData}
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
        selectedTab={selectedTab}
      />
      <GrievancesTable filter={appliedFilter} selectedTab={selectedTab} />
    </>
  );
};
export default withErrorBoundary(GrievancesTablePage, 'GrievancesTablePage');
