import { useConfirmation } from '@core/ConfirmationDialog';
import { LoadingComponent } from '@core/LoadingComponent';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button, Tooltip, Typography } from '@mui/material';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { PaginatedGrievanceTicketListList } from '@restgenerated/models/PaginatedGrievanceTicketListList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import { GRIEVANCE_CATEGORIES } from '@utils/constants';
import { getFilterFromQueryParams, showApiErrorMessages } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { NaComparisonPanel } from './NaComparisonPanel';
import { NaTicketsFilters } from './NaTicketsFilters';
import { NaTicketsList } from './NaTicketsList';
import { buildExecutePayload } from './naPayload';
import { isDecisionResolved } from './naRoleUtils';
import { NaTicketDecision } from './naTypes';

// Needs Adjudication category id (see GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION = '8')
const NEEDS_ADJUDICATION_CATEGORY = Number(
  GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION,
) as 8;

const initialFilter = {
  search: '',
  documentType: '',
  documentNumber: '',
  createdAtBefore: '',
  createdAtAfter: '',
  scoreMin: '',
  scoreMax: '',
  preferredLanguage: '',
  priority: '',
  urgency: '',
  program: '',
  admin1: '',
  admin2: '',
  issueType: '',
  areaScope: 'all',
};

interface NaTicketsManagementProps {
  onBack: () => void;
}

export const NaTicketsManagement = ({
  onBack,
}: NaTicketsManagementProps): ReactElement => {
  const { t } = useTranslation();
  const { businessAreaSlug, isAllPrograms } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const queryClient = useQueryClient();
  const location = useLocation();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  // Session-local adjudication decisions per ticket id (not persisted).
  const [decisions, setDecisions] = useState<Record<string, NaTicketDecision>>(
    {},
  );

  const setDecision = (ticketId: string, decision: NaTicketDecision): void =>
    setDecisions((prev) => ({ ...prev, [ticketId]: decision }));

  const clearDecision = (ticketId: string): void =>
    setDecisions((prev) => {
      const next = { ...prev };
      delete next[ticketId];
      return next;
    });

  // Records the operator's replacement pick for one required role.
  const setReassignment = (
    ticketId: string,
    key: string,
    newIndividual: { id: string; fullName?: string },
  ): void =>
    setDecisions((prev) => {
      const decision = prev[ticketId];
      const assignment = decision?.reassignments[key];
      if (!assignment) return prev;
      return {
        ...prev,
        [ticketId]: {
          ...decision,
          reassignments: {
            ...decision.reassignments,
            [key]: {
              ...assignment,
              newIndividual: newIndividual.id,
              newIndividualName: newIndividual.fullName,
            },
          },
        },
      };
    });

  const managedCount = Object.keys(decisions).length;
  const unresolvedCount = Object.values(decisions).filter(
    (decision) => !isDecisionResolved(decision),
  ).length;

  const { mutate: executeBatch, isPending: isFinalizing } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasGrievanceTicketsBulkNeedsAdjudicationCreate({
        businessAreaSlug,
        formData: { tickets: buildExecutePayload(decisions) },
      }),
    onSuccess: () => {
      showMessage(t('{{count}} ticket(s) finalized', { count: managedCount }));
      setDecisions({});
      queryClient.invalidateQueries({
        queryKey: restQueryKey(RestService.restBusinessAreasGrievanceTicketsList),
      });
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasGrievanceTicketsCountRetrieve,
        ),
      });
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasGrievanceTicketsRetrieve,
        ),
      });
    },
    // The batch is rejected whole and nothing changes server-side, so keep the
    // decisions on screen for the operator to fix and retry.
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const handleFinalize = (): void => {
    confirm({
      title: t('Finalize'),
      content: t(
        'You are about to finalize {{count}} ticket(s). They will be closed and this cannot be undone.',
        { count: managedCount },
      ),
    }).then(
      () => executeBatch(),
      () => undefined,
    );
  };

  const queryVariables = useMemo(
    () => ({
      search: (appliedFilter.search as string).trim(),
      documentType: appliedFilter.documentType,
      documentNumber: (appliedFilter.documentNumber as string).trim(),
      createdAtBefore: appliedFilter.createdAtBefore,
      createdAtAfter: appliedFilter.createdAtAfter,
      scoreMin: appliedFilter.scoreMin,
      scoreMax: appliedFilter.scoreMax,
      preferredLanguage: appliedFilter.preferredLanguage,
      priority:
        appliedFilter.priority === 'Not Set' ? 0 : appliedFilter.priority,
      urgency: appliedFilter.urgency === 'Not Set' ? 0 : appliedFilter.urgency,
      admin1: appliedFilter.admin1,
      admin2: appliedFilter.admin2,
      issueType: appliedFilter.issueType,
      program: isAllPrograms ? appliedFilter.program : undefined,
      isCrossArea: appliedFilter.areaScope === 'cross-area' ? true : null,
    }),
    [appliedFilter, isAllPrograms],
  );

  const { data: listData, isLoading: listLoading } =
    useQuery<PaginatedGrievanceTicketListList>({
      queryKey: restQueryKey(RestService.restBusinessAreasGrievanceTicketsList, {
        businessAreaSlug,
        category: NEEDS_ADJUDICATION_CATEGORY,
        page,
        rowsPerPage,
        queryVariables,
      }),
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsList(
          createApiParams(
            {
              businessAreaSlug,
              category: NEEDS_ADJUDICATION_CATEGORY,
              limit: rowsPerPage,
              offset: page * rowsPerPage,
              ordering: '-created_at',
            },
            queryVariables,
          ),
        ),
    });

  const { data: countData } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasGrievanceTicketsCountRetrieve,
      {
        businessAreaSlug,
        category: NEEDS_ADJUDICATION_CATEGORY,
        queryVariables,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsCountRetrieve(
        createApiParams(
          {
            businessAreaSlug,
            category: NEEDS_ADJUDICATION_CATEGORY,
          },
          queryVariables,
        ),
      ),
  });

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<GrievanceChoices>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve,
        { businessAreaSlug },
      ),
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
          businessAreaSlug,
        }),
    });

  const results = useMemo(() => listData?.results ?? [], [listData]);

  // Default the selection to the first ticket on the current page.
  useEffect(() => {
    if (results.length === 0) {
      setSelectedTicketId(null);
      return;
    }
    const stillVisible = results.some((r) => r.id === selectedTicketId);
    if (!stillVisible) {
      setSelectedTicketId(results[0].id);
    }
  }, [results, selectedTicketId]);

  return (
    <>
      <PageHeader
        title={t('NA Tickets Management')}
        breadCrumbs={[
          { title: t('Grievance Tickets List'), handleClick: onBack },
        ]}
        handleBack={onBack}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Typography variant="body2" data-cy="na-tickets-managed-count">
            {t('Tickets managed')}: {managedCount}
          </Typography>
          <Tooltip
            title={
              unresolvedCount > 0
                ? t(
                    '{{count}} ticket(s) need a role reassignment before finalizing',
                    { count: unresolvedCount },
                  )
                : ''
            }
            data-cy="na-finalize-blocked-tooltip"
          >
            <span>
              <Button
                variant="contained"
                color="primary"
                disabled={
                  managedCount === 0 || unresolvedCount > 0 || isFinalizing
                }
                onClick={handleFinalize}
                data-cy="button-na-finalize"
              >
                {t('Finalize')}
              </Button>
            </span>
          </Tooltip>
        </Box>
      </PageHeader>
      {choicesLoading ? (
        <LoadingComponent />
      ) : (
        <>
          <NaTicketsFilters
            filter={filter}
            choicesData={choicesData}
            setFilter={setFilter}
            initialFilter={initialFilter}
            appliedFilter={appliedFilter}
            setAppliedFilter={(f) => {
              setAppliedFilter(f);
              setPage(0);
            }}
          />
          <Box
            sx={{ display: 'flex', alignItems: 'stretch', p: 5, gap: 5 }}
          >
            <Box sx={{ width: '40%', minWidth: 360 }}>
              <NaTicketsList
                tickets={results}
                isLoading={listLoading}
                choicesData={choicesData}
                selectedTicketId={selectedTicketId}
                decisions={decisions}
                onSelect={setSelectedTicketId}
                page={page}
                rowsPerPage={rowsPerPage}
                count={countData?.count ?? 0}
                onPageChange={setPage}
                onRowsPerPageChange={(value) => {
                  setRowsPerPage(value);
                  setPage(0);
                }}
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <NaComparisonPanel
                ticketId={selectedTicketId}
                decision={
                  selectedTicketId ? decisions[selectedTicketId] : undefined
                }
                onDecide={(decision) => {
                  if (selectedTicketId) setDecision(selectedTicketId, decision);
                }}
                onReassign={(key, newIndividual) => {
                  if (selectedTicketId)
                    setReassignment(selectedTicketId, key, newIndividual);
                }}
                onClear={() => {
                  if (selectedTicketId) clearDecision(selectedTicketId);
                }}
              />
            </Box>
          </Box>
        </>
      )}
    </>
  );
};
