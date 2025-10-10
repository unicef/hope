import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { createApiParams } from '@utils/apiUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { headCells } from './LookUpTargetPopulationTableHeadCellsSurveys';
import { LookUpTargetPopulationTableRowSurveys } from './LookUpTargetPopulationTableRowSurveys';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';

interface LookUpTargetPopulationTableSurveysProps {
  filter;
  canViewDetails: boolean;
  enableRadioButton?: boolean;
  selectedTargetPopulation?;
  handleChange?;
  noTableStyling?;
  noTitle?;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

export function LookUpTargetPopulationTableSurveys({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedTargetPopulation,
  handleChange,
  noTableStyling,
  noTitle,
}: LookUpTargetPopulationTableSurveysProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  const [page, setPage] = useState(0);

  const initialQueryVariables = useMemo(
    () => ({
      totalHouseholdsCountWithValidPhoneNoMin:
        filter.totalHouseholdsCountMin || 0,
      totalHouseholdsCountWithValidPhoneNoMax:
        filter.totalHouseholdsCountMax || null,
      status: filter.status,
      businessArea,
      createdAtRange: JSON.stringify({
        min: filter.createdAtRangeMin || null,
        max: filter.createdAtRangeMax || null,
      }),
      statusNot: PaymentPlanStatusEnum.OPEN,
      isTargetPopulation: true,
      businessAreaSlug: businessArea,
      programSlug: programId,
      page,
    }),
    [
      filter.totalHouseholdsCountMin,
      filter.totalHouseholdsCountMax,
      filter.status,
      businessArea,
      filter.createdAtRangeMin,
      filter.createdAtRangeMax,
      programId,
      page,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: paymentPlansData,
    isLoading,
    error,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: [
      'businessAreasProgramsTargetPopulationsList',
      queryVariables,
      businessArea,
      programId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  // Count query, enabled only on page 0
  const { data: countData } = useQuery({
    queryKey: [
      'businessAreasProgramsTargetPopulationsCount',
      queryVariables,
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsCountRetrieve(
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
    if (page === 0 && typeof countData?.count === 'number') {
      setPersistedCount(countData.count);
    }
  }, [page, countData]);

  const itemsCount = persistedCount;

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalRestTable
        title={noTitle ? null : t('Target Populations')}
        headCells={enableRadioButton ? headCells : headCells.slice(1)}
        rowsPerPageOptions={[10, 15, 20]}
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        data={paymentPlansData}
        isLoading={isLoading}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        itemsCount={itemsCount}
        page={page}
        setPage={setPage}
        renderRow={(row: TargetPopulationList) => (
          <LookUpTargetPopulationTableRowSurveys
            radioChangeHandler={enableRadioButton && handleRadioChange}
            selectedTargetPopulation={selectedTargetPopulation}
            key={row.id}
            targetPopulation={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    renderTable()
  );
}
