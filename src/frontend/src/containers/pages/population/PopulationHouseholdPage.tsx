import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { HouseholdFilters } from '@components/population/HouseholdFilter';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { HouseholdTable } from '@containers/tables/population/HouseholdTable/HouseholdTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';

function PopulationHouseholdPage(): ReactElement {
  const location = useLocation();
  const { businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const initialFilter = {
    search: '',
    documentType: choicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: '',
    residenceStatus: '',
    admin1: '',
    admin2: '',
    householdSizeMin: '',
    householdSizeMax: '',
    orderBy: 'unicef_id',
    withdrawn: '',
    rdiId: '',
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  const permissions = usePermissions();

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST, permissions))
    return (
      <PermissionDenied
        permission={PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST}
      />
    );

  if (!choicesData) return null;

  return (
    <>
      <PageHeader title={beneficiaryGroup?.groupLabelPlural} />
      <HouseholdFilters
        filter={filter}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={(newFilter) => {
          setAppliedFilter(newFilter);
          setShouldScroll(true);
        }}
      />
      <Box
        display="flex"
        flexDirection="column"
        data-cy="page-details-container"
        ref={tableRef}
      >
        <HouseholdTable
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            permissions,
          )}
        />
      </Box>
    </>
  );
}
export default withErrorBoundary(
  PopulationHouseholdPage,
  'PopulationHouseholdPage',
);
