import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { HouseholdFilters } from '@components/population/HouseholdFilter';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { HouseholdTable } from '@containers/tables/population/HouseholdTable/HouseholdTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

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
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const permissions = usePermissions();

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST, permissions))
    return <PermissionDenied />;

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
        setAppliedFilter={setAppliedFilter}
      />
      <Box
        display="flex"
        flexDirection="column"
        data-cy="page-details-container"
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
