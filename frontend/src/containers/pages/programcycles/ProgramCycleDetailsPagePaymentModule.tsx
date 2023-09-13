import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import {
  useProgramCycleQuery,
  useProgrammeChoiceDataQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { ProgramCycleDetailsHeaderPaymentModule } from '../../../components/paymentmodule/ProgramCycleDetailsPaymentModule/ProgramCycleDetailsHeaderPaymentModule';
import { ProgramCycleDetailsPaymentModule } from '../../../components/paymentmodule/ProgramCycleDetailsPaymentModule/ProgramCycleDetailsPaymentModule';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  choicesToDict,
  getFilterFromQueryParams,
  isPermissionDeniedError,
} from '../../../utils/utils';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { PaymentPlansFiltersProgramCycle } from '../../tables/paymentmodule/ProgramCycles/PaymentPlansTableProgramCycle/PaymentPlansFiltersProgramCycle';
import { PaymentPlansTableProgramCycle } from '../../tables/paymentmodule/ProgramCycles/PaymentPlansTableProgramCycle/PaymentPlansTableProgramCycle';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
  isFollowUp: false,
};

export const ProgramCycleDetailsPagePaymentModule = (): React.ReactElement => {
  const { id } = useParams();
  const location = useLocation();
  const permissions = usePermissions();
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const { data: programCycleData, loading, error } = useProgramCycleQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: programChoiceData,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();

  if (loading || choicesLoading) return <LoadingComponent />;
  if (permissions === null || !programCycleData || !programChoiceData)
    return null;

  if (
    !hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied />;

  const { programCycle } = programCycleData;

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(programChoiceData.programCycleStatusChoices);

  return (
    <Box display='flex' flexDirection='column'>
      <ProgramCycleDetailsHeaderPaymentModule
        programCycle={programCycle}
        permissions={permissions}
      />
      <ProgramCycleDetailsPaymentModule
        programCycle={programCycle}
        statusChoices={statusChoices}
      />
      <TableWrapper>
        <PaymentPlansFiltersProgramCycle
          filter={filter}
          setFilter={setFilter}
          initialFilter={initialFilter}
          appliedFilter={appliedFilter}
          setAppliedFilter={setAppliedFilter}
        />
      </TableWrapper>
      <TableWrapper>
        <PaymentPlansTableProgramCycle
          programCycle={programCycle}
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.PM_VIEW_DETAILS,
            permissions,
          )}
        />
      </TableWrapper>

      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={programCycle.id} />
      )}
    </Box>
  );
};
