import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
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
import { createApiParams } from '@utils/apiUtils';
import { programCycleStatusToColor, showApiErrorMessages } from '@utils/utils';
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
  const { businessArea, programId, isAllPrograms } = useBaseUrl();
  // Controlled pagination state
  const [page, setPage] = useState(0);
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

  // Don't fetch data when viewing "all programs"
  const shouldFetchData = Boolean(!isAllPrograms && program?.id);

  const rowsPerPage =
    queryVariables && typeof queryVariables.limit === 'number'
      ? queryVariables.limit
      : 5;
  const { data, refetch, error, isLoading } =
    useQuery<PaginatedProgramCycleListList>({
      queryKey: [
        'programCycles',
        queryVariables,
        businessArea,
        programId,
        page,
        rowsPerPage,
      ],
      queryFn: () => {
        return RestService.restBusinessAreasProgramsCyclesList(
          createApiParams(
            { businessAreaSlug: businessArea, programSlug: programId },
            { ...queryVariables, offset: page * rowsPerPage },
            { withPagination: true },
          ),
        );
      },
      enabled: shouldFetchData,
    });

  const { data: dataProgramCyclesCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsCyclesCountRetrieve',
      programId,
      businessArea,
      queryVariables,
      page,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsCyclesCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
    enabled: page === 0,
  });

  // Persist count after fetching on page 0
  const [persistedCount, setPersistedCount] = useState<number | undefined>(
    undefined,
  );
  useEffect(() => {
    if (page === 0 && typeof dataProgramCyclesCount?.count === 'number') {
      setPersistedCount(dataProgramCyclesCount.count);
    }
  }, [page, dataProgramCyclesCount]);

  const itemsCount = persistedCount;

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
          exact: false,
        });
        await queryClient.invalidateQueries({
          queryKey: ['programCycles', queryVariables, businessArea, programId],
          exact: false,
        });
      },
      mutationKey: ['finishProgramCycle', businessArea, program.id],
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
          queryKey: ['programCycles', businessArea, program.slug],
          exact: false,
        });
        await queryClient.invalidateQueries({
          queryKey: ['programCycles', queryVariables, businessArea, programId],
          exact: false,
        });
      },
      mutationKey: ['reactivateProgramCycle', businessArea, program.id],
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
      showApiErrorMessages(e, showMessage);
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
      itemsCount={itemsCount}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      page={page}
      setPage={setPage}
    />
  );
};
