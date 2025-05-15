import {
  finishProgramCycle,
  reactivateProgramCycle,
} from '@api/programCycleApi';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { createApiParams } from '@utils/apiUtils';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Button } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { PaginatedProgramCycleListList } from '@restgenerated/models/PaginatedProgramCycleListList';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { decodeIdString, programCycleStatusToColor } from '@utils/utils';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ProgramCyclesTablePaymentModuleProps {
  program;
  filters;
  adjustedHeadCells;
}

export const ProgramCyclesTablePaymentModule = ({
  program,
  filters,
  adjustedHeadCells,
}: ProgramCyclesTablePaymentModuleProps) => {
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const [queryVariables, setQueryVariables] = useState({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
    businessAreaSlug: businessArea,
    programSlug: programId,
    ...filters,
  });

  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const { data, refetch, error, isLoading } =
    useQuery<PaginatedProgramCycleListList>({
      queryKey: ['programCycles', queryVariables, businessArea, programId],
      queryFn: () => {
        return RestService.restBusinessAreasProgramsCyclesList(
          createApiParams(
            { businessAreaSlug: businessArea, programSlug: programId },
            queryVariables,
            { withPagination: true },
          ),
        );
      },
    });

  const { data: dataProgramCyclesCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsCyclesCountRetrieve',
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsCyclesCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
      }),
  });

  const { mutateAsync: finishMutation, isPending: isPendingFinishing } =
    useMutation({
      mutationFn: async ({ programCycleId }: { programCycleId: string }) => {
        return finishProgramCycle(businessArea, program.id, programCycleId);
      },
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: ['programCycles', businessArea, program.id],
        });
      },
    });

  const { mutateAsync: reactivateMutation, isPending: isPendingReactivation } =
    useMutation({
      mutationFn: async ({ programCycleId }: { programCycleId: string }) => {
        return reactivateProgramCycle(businessArea, program.id, programCycleId);
      },
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: ['programCycles', businessArea, program.id],
        });
      },
    });

  useEffect(() => {
    setQueryVariables((oldVariables) => ({ ...oldVariables, ...filters }));
  }, [filters]);

  useEffect(() => {
    void refetch();
  }, [queryVariables, refetch]);

  const finishAction = async (programCycle: ProgramCycleList) => {
    try {
      const decodedProgramCycleId = decodeIdString(programCycle.id);
      await finishMutation({ programCycleId: decodedProgramCycleId });
      showMessage(t('Programme Cycle Finished'));
    } catch (e) {
      if (e.data && Array.isArray(e.data)) {
        e.data.forEach((message: string) => showMessage(message));
      }
    }
  };

  const reactivateAction = async (programCycle: ProgramCycleList) => {
    try {
      const decodedProgramCycleId = decodeIdString(programCycle.id);
      await reactivateMutation({ programCycleId: decodedProgramCycleId });
      showMessage(t('Programme Cycle Reactivated'));
    } catch (e) {
      if (e.data && Array.isArray(e.data)) {
        e.data.forEach((message: string) => showMessage(message));
      }
    }
  };

  const renderRow = (row: ProgramCycleList): ReactElement => (
    <ClickableTableRow key={row.id} data-cy="program-cycle-row">
      <TableCell data-cy="program-cycle-title">
        <BlackLink to={`./${row.id}`}>{row.title}</BlackLink>
      </TableCell>
      <TableCell data-cy="program-cycle-status">
        <StatusBox
          status={row.status}
          statusToColor={programCycleStatusToColor}
        />
      </TableCell>
      <TableCell
        align="right"
        data-cy="program-cycle-total-entitled-quantity-usd"
      >
        {row.totalEntitledQuantityUsd || '-'}
      </TableCell>
      <TableCell data-cy="program-cycle-start-date">
        <UniversalMoment>{row.startDate}</UniversalMoment>
      </TableCell>
      <TableCell data-cy="program-cycle-end-date">
        <UniversalMoment>{row.endDate}</UniversalMoment>
      </TableCell>
      <TableCell data-cy="program-cycle-details-btn">
        {row.status === 'Finished' && (
          <Button
            onClick={() => reactivateAction(row)}
            variant="text"
            disabled={isPendingReactivation}
          >
            {t('REACTIVATE')}
          </Button>
        )}
        {row.status === 'Active' && (
          <Button
            onClick={() => finishAction(row)}
            variant="text"
            disabled={isPendingFinishing}
          >
            {t('FINISH')}
          </Button>
        )}
      </TableCell>
    </ClickableTableRow>
  );

  return (
    <UniversalRestTable
      title="Programme Cycles"
      renderRow={renderRow}
      headCells={adjustedHeadCells}
      itemsCount={dataProgramCyclesCount?.count}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
};
