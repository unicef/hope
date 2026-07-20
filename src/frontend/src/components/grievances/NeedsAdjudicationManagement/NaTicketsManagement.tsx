import { LoadingComponent } from '@core/LoadingComponent';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Button } from '@mui/material';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { PaginatedGrievanceTicketListList } from '@restgenerated/models/PaginatedGrievanceTicketListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { GRIEVANCE_CATEGORIES } from '@utils/constants';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { NaComparisonPanel } from './NaComparisonPanel';
import { NaTicketsFilters } from './NaTicketsFilters';
import { NaTicketsList } from './NaTicketsList';

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
      program: isAllPrograms ? appliedFilter.program : undefined,
      isCrossArea: appliedFilter.areaScope === 'cross-area' ? true : null,
    }),
    [appliedFilter, isAllPrograms],
  );

  const { data: listData, isLoading: listLoading } =
    useQuery<PaginatedGrievanceTicketListList>({
      queryKey: [
        'naTicketsManagementList',
        businessAreaSlug,
        page,
        rowsPerPage,
        queryVariables,
      ],
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
    queryKey: ['naTicketsManagementCount', businessAreaSlug, queryVariables],
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
      queryKey: ['businessAreasGrievanceTicketsChoices', businessAreaSlug],
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
        {/* TODO: wire FINALIZE to the needs-adjudication resolution flow */}
        <Button
          variant="contained"
          color="primary"
          disabled
          data-cy="button-na-finalize"
        >
          {t('Finalize')}
        </Button>
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
          <Box display="flex" alignItems="stretch" p={5} gap={5}>
            <Box width="40%" minWidth={360}>
              <NaTicketsList
                tickets={results}
                isLoading={listLoading}
                choicesData={choicesData}
                selectedTicketId={selectedTicketId}
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
            <Box flex={1}>
              <NaComparisonPanel ticketId={selectedTicketId} />
            </Box>
          </Box>
        </>
      )}
    </>
  );
};
