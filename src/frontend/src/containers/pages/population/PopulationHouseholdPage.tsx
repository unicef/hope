import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { HouseholdFilters } from '@components/population/HouseholdFilter';
import { useHouseholdChoiceDataQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { HouseholdTable } from '../../tables/population/HouseholdTable';
import withErrorBoundary from '@components/core/withErrorBoundary';

function PopulationHouseholdPage(): ReactElement {
  const location = useLocation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { data: choicesData, loading: choicesLoading } =
    useHouseholdChoiceDataQuery({
      fetchPolicy: 'cache-first',
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

  const { businessArea } = useBaseUrl();
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
          businessArea={businessArea}
          choicesData={choicesData}
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
