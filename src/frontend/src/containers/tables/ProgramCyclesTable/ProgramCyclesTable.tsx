import { ReactElement, useEffect, useState } from 'react';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { StatusBox } from '@core/StatusBox';
import {
  decodeIdString,
  formatCurrencyWithSymbol,
  programCycleStatusToColor,
} from '@utils/utils';
import { UniversalMoment } from '@core/UniversalMoment';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/tables/ProgramCyclesTablePaymentModule/HeadCells';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { finishProgramCycle, ProgramCyclesQuery } from '@api/programCycleApi';
import { PaginatedProgramCycleListList } from '@restgenerated/models/PaginatedProgramCycleListList';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { BlackLink } from '@core/BlackLink';
import { useTranslation } from 'react-i18next';
import { Button } from '@mui/material';
import { useSnackbar } from '@hooks/useSnackBar';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';

interface ProgramCyclesTablePaymentModuleProps {
  program;
  filters;
}

const ProgramCyclesTablePaymentModule = ({
  program,
  filters,
}: ProgramCyclesTablePaymentModuleProps) => {
  const { showMessage } = useSnackbar();
  const [queryVariables, setQueryVariables] = useState<ProgramCyclesQuery>({
    offset: 0,
    limit: 5,
    ordering: 'created_at',
    ...filters,
  });

  const { businessArea, programId } = useBaseUrl();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const { data, refetch, error, isLoading } =
    useQuery<PaginatedProgramCycleListList>({
      queryKey: ['programCycles', businessArea, program.id, queryVariables],
      queryFn: () => {
        return RestService.restBusinessAreasProgramsCyclesList(
          createApiParams(
            {
              businessAreaSlug: businessArea,
              programSlug: program.id,
            },
            queryVariables,
            { withPagination: true },
          ),
        );
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
      mutationFn: ({
        businessAreaSlug,
        id,
        programSlug,
      }: {
        businessAreaSlug: string;
        id: string;
        programSlug: string;
      }) =>
        RestService.restBusinessAreasProgramsCyclesReactivateCreate({
          businessAreaSlug,
          id,
          programSlug,
        }),
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
      await reactivateMutation({
        businessAreaSlug: businessArea,
        id: decodedProgramCycleId,
        programSlug: programId,
      });
      showMessage(t('Programme Cycle Reactivated'));
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
        {formatCurrencyWithSymbol(row.totalEntitledQuantityUsd)}
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
      headCells={headCells}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
};

export default withErrorBoundary(
  ProgramCyclesTablePaymentModule,
  'ProgramCyclesTablePaymentModule',
);
