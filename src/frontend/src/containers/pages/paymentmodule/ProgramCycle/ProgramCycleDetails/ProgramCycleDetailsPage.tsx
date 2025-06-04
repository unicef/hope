import { ReactElement, useState } from 'react';
import { decodeIdString, getFilterFromQueryParams } from '@utils/utils';
import { useQuery } from '@tanstack/react-query';
import { fetchProgramCycle } from '@api/programCycleApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useLocation, useParams } from 'react-router-dom';
import { ProgramCycleDetailsHeader } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsHeader';
import { ProgramCycleDetailsSection } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsSection';
import { TableWrapper } from '@core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { PaymentPlansTable } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansTable';
import { PaymentPlansFilters } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansFilters';
import withErrorBoundary from '@components/core/withErrorBoundary';

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

  const decodedProgramCycleId = decodeIdString(programCycleId);

  const { data, isLoading } = useQuery({
    queryKey: [
      'programCyclesDetails',
      businessArea,
      programId,
      decodedProgramCycleId,
    ],
    queryFn: async () => {
      return fetchProgramCycle(businessArea, programId, decodedProgramCycleId);
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
