import React, { ReactElement, useEffect, useState } from 'react';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { StatusBox } from '@core/StatusBox';
import { decodeIdString, programCycleStatusToColor } from '@utils/utils';
import { UniversalMoment } from '@core/UniversalMoment';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/tables/ProgramCyclesTable/HeadCells';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  fetchProgramCycles,
  finishProgramCycle,
  ProgramCycle,
  ProgramCyclesQuery,
  reactivateProgramCycle,
} from '@api/programCycleApi';
import { BlackLink } from '@core/BlackLink';
import { useTranslation } from 'react-i18next';
import { Button } from '@mui/material';
import { useSnackbar } from '@hooks/useSnackBar';

interface ProgramCyclesTableProps {
  program;
  filters;
}

export const ProgramCyclesTable = ({
  program,
  filters,
}: ProgramCyclesTableProps) => {
  const { showMessage } = useSnackbar();
  const [queryVariables, setQueryVariables] = useState<ProgramCyclesQuery>({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
    ...filters,
  });

  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const { data, refetch, error, isLoading } = useQuery({
    queryKey: ['programCycles', businessArea, program.id, queryVariables],
    queryFn: async () => {
      return fetchProgramCycles(businessArea, program.id, queryVariables);
    },
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

  const finishAction = async (programCycle: ProgramCycle) => {
    try {
      const decodedProgramCycleId = decodeIdString(programCycle.id);
      await finishMutation({ programCycleId: decodedProgramCycleId });
      showMessage(t('Programme Cycle Finished'));
    } catch (e) {
      e.data?.forEach((message: string) => showMessage(message));
    }
  };

  const reactivateAction = async (programCycle: ProgramCycle) => {
    try {
      const decodedProgramCycleId = decodeIdString(programCycle.id);
      await reactivateMutation({ programCycleId: decodedProgramCycleId });
      showMessage(t('Programme Cycle Reactivated'));
    } catch (e) {
      e.data?.forEach((message: string) => showMessage(message));
    }
  };

  const renderRow = (row: ProgramCycle): ReactElement => (
    <ClickableTableRow key={row.id} data-cy="program-cycle-row">
      <TableCell data-cy="program-cycle-id">
        <BlackLink to={`./${row.id}`}>{row.unicef_id}</BlackLink>
      </TableCell>
      <TableCell data-cy="program-cycle-title">{row.title}</TableCell>
      <TableCell data-cy="program-cycle-status">
        <StatusBox
          status={row.status}
          statusToColor={programCycleStatusToColor}
        />
      </TableCell>
      <TableCell data-cy="program-cycle-total-entitled-quantity">
        {row.total_entitled_quantity_usd || '-'}
      </TableCell>
      <TableCell data-cy="program-cycle-start-date">
        <UniversalMoment>{row.start_date}</UniversalMoment>
      </TableCell>
      <TableCell data-cy="program-cycle-end-date">
        <UniversalMoment>{row.end_date}</UniversalMoment>
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
      headCells={headCells}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
};
