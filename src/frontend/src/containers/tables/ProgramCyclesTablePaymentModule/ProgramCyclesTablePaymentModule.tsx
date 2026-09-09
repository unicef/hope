import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Button } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { PaginatedProgramCycleListList } from '@restgenerated/models/PaginatedProgramCycleListList';
import type { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import {
  programCycleStatusToColor,
  showApiErrorMessages,
  formatFigure,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useEffect, useState } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTranslation } from 'react-i18next';
import AddNewProgramCycle from '@containers/tables/ProgramCycle/NewProgramCycle/AddNewProgramCycle';

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
    programCode: programId,
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
  const programCyclesListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    { ...queryVariables, offset: page * rowsPerPage },
    { withPagination: true },
  );
  const { data, refetch, error, isLoading, isFetching } =
    useQuery<PaginatedProgramCycleListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsCyclesList,
        programCyclesListParams,
      ),
      queryFn: () => {
        return RestService.restBusinessAreasProgramsCyclesList(
          programCyclesListParams,
        );
      },
      placeholderData: keepPreviousData,
      enabled: shouldFetchData,
    });

  const programCyclesCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    queryVariables,
  );
  const { data: dataProgramCyclesCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsCyclesCountRetrieve,
      programCyclesCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsCyclesCountRetrieve(
        programCyclesCountParams,
      ),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, dataProgramCyclesCount);

  const { mutateAsync: finishMutation, isPending: isPendingFinishing } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programCode,
      }: {
        businessAreaSlug: string;
        id: string;
        programCode: string;
      }) =>
        RestService.restBusinessAreasProgramsCyclesFinishCreate({
          businessAreaSlug,
          id,
          programCode,
        }),
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsCyclesList,
          ),
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
        programCode,
      }: {
        businessAreaSlug: string;
        id: string;
        programCode: string;
      }) =>
        RestService.restBusinessAreasProgramsCyclesReactivateCreate({
          businessAreaSlug,
          id,
          programCode,
        }),
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsCyclesList,
          ),
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
        programCode: programId,
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
        programCode: programId,
      });
      showMessage(t('Programme Cycle Reactivated'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const actions = [
    <AddNewProgramCycle
      key="add-new"
      program={program}
      lastProgramCycle={(data?.results || [])[(data?.results || []).length - 1]}
    />,
  ];

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
        {formatFigure(row.totalEntitledQuantityUsd)}
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
      actions={actions}
      renderRow={renderRow}
      headCells={adjustedHeadCells}
      itemsCount={itemsCount}
      data={data}
      error={error}
      isLoading={isLoading}
      isFetching={isFetching}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      page={page}
      setPage={setPage}
    />
  );
};
