import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlansFilters } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansFilters';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { ProgramCycleDetailsHeader } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsHeader';
import { ProgramCycleDetailsSection } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsSection';
import { TableWrapper } from '@core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
  isFollowUp: false,
};

export const ProgramCycleDetailsPage = (): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const { programCycleId } = useParams();
  const location = useLocation();
  const permissions = usePermissions();

  const { data, isLoading } = useQuery<ProgramCycleList>({
    queryKey: ['programCyclesDetails', businessArea, programCycleId, programId],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsCyclesRetrieve({
        businessAreaSlug: businessArea,
        id: programCycleId,
        programSlug: programId,
      });
    },
  });

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (isLoading) return null;

  return (
    <>
      <ProgramCycleDetailsHeader programCycle={data} />
      <ProgramCycleDetailsSection programCycle={data} />
      <TableWrapper>
        <PaymentPlansFilters
          filter={filter}
          setFilter={setFilter}
          initialFilter={initialFilter}
          appliedFilter={appliedFilter}
          setAppliedFilter={setAppliedFilter}
        />
      </TableWrapper>
      <TableWrapper>
        <PaymentPlansTable
          programCycle={data}
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.PM_VIEW_DETAILS,
            permissions,
          )}
        />
      </TableWrapper>
    </>
  );
};
export default withErrorBoundary(
  ProgramCycleDetailsPage,
  'ProgramCycleDetailsPage',
);
