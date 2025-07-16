import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/tables/ProgramCyclesTablePaymentModule/HeadCells';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Button } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { PaginatedProgramCycleListList } from '@restgenerated/models/PaginatedProgramCycleListList';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import {
  formatCurrencyWithSymbol,
  programCycleStatusToColor,
  showApiErrorMessages,
} from '@utils/utils';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ProgramCyclesTablePaymentModuleProps {
  program;
  filters;
}

const ProgramCyclesTablePaymentModule = ({
  program,
  filters,
}: ProgramCyclesTablePaymentModuleProps) => {
  const { showMessage } = useSnackbar();
  const [queryVariables, setQueryVariables] = useState<ProgramCycleList>({
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
      queryKey: ['programCycles', businessArea, program.slug, queryVariables],
      queryFn: () => {
        return RestService.restBusinessAreasProgramsCyclesList(
          createApiParams(
            {
              businessAreaSlug: businessArea,
              programSlug: program.slug,
            },
            queryVariables,
            { withPagination: true },
          ),
        );
      },
    });

  const { mutateAsync: finishMutation, isPending: isPendingFinishing } =
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
        RestService.restBusinessAreasProgramsCyclesFinishCreate({
          businessAreaSlug,
          id,
          programSlug,
        }),
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: ['programCycles', businessArea, program.slug],
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
      }) => {
        return RestService.restBusinessAreasProgramsCyclesReactivateCreate({
          businessAreaSlug,
          id,
          programSlug,
        });
      },

      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: ['programCycles', businessArea, program.slug],
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
      await finishMutation({
        businessAreaSlug: businessArea,
        id: programCycle.id,
        programSlug: programId,
      });
      showMessage(t('Programme Cycle Finished'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const reactivateAction = async (programCycle: ProgramCycleList) => {
    try {
      await reactivateMutation({
        businessAreaSlug: businessArea,
        id: programCycle.id,
        programSlug: programId,
      });
      showMessage(t('Programme Cycle Reactivated'));
    } catch (e) {
      showApiErrorMessages(e, showMessage, t('Failed to  reactivate cycle.'));
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
