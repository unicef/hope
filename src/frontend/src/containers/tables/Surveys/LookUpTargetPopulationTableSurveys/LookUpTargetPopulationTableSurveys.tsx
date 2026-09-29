import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { createApiParams } from '@utils/apiUtils';
import { restQueryKey } from '@utils/queryKeys';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { headCells } from './LookUpTargetPopulationTableHeadCellsSurveys';
import { LookUpTargetPopulationTableRowSurveys } from './LookUpTargetPopulationTableRowSurveys';
import type { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import type { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';

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

  const filterVariables = useMemo(
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
      programCode: programId,
    }),
    [
      filter.totalHouseholdsCountMin,
      filter.totalHouseholdsCountMax,
      filter.status,
      businessArea,
      filter.createdAtRangeMin,
      filter.createdAtRangeMax,
      programId,
    ],
  );

  const table = useTableState({
    rowsPerPageOptions: [10, 15, 20],
    defaultOrderBy: 'createdAt',
    defaultOrderDirection: 'desc',
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

  const targetPopulationsListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    listVariables,
  );
  const {
    data: paymentPlansData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsTargetPopulationsList,
      targetPopulationsListParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsList(
        targetPopulationsListParams,
      );
    },
    placeholderData: keepPreviousData,
  });

  // Count query, enabled only on page 0
  const targetPopulationsCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    filterVariables,
  );
  const { data: countData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsTargetPopulationsCountRetrieve,
      targetPopulationsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsCountRetrieve(
        targetPopulationsCountParams,
      ),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, countData);

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalRestTable
        title={noTitle ? null : t('Target Populations')}
        headCells={enableRadioButton ? headCells : headCells.slice(1)}
        data={paymentPlansData}
        isLoading={isLoading}
        isFetching={isFetching}
        error={error}
        tableState={table}
        itemsCount={itemsCount}
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
