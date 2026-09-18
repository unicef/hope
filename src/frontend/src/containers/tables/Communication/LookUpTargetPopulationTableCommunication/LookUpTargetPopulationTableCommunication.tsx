import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from './LookUpTargetPopulationTableHeadCellsCommunication';
import { LookUpTargetPopulationTableRowCommunication } from './LookUpTargetPopulationTableRowCommunication';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import type { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import type { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface LookUpTargetPopulationTableCommunicationProps {
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

const LookUpTargetPopulationTableCommunication = ({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedTargetPopulation,
  handleChange,
  noTableStyling,
  noTitle,
}: LookUpTargetPopulationTableCommunicationProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  const filterVariables = useMemo(
    () => ({
      totalHouseholdsCountWithValidPhoneNoMin:
        filter.totalHouseholdsCountWithValidPhoneNoMin || 0,
      totalHouseholdsCountWithValidPhoneNoMax:
        filter.totalHouseholdsCountWithValidPhoneNoMax || null,
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
      filter.totalHouseholdsCountWithValidPhoneNoMin,
      filter.totalHouseholdsCountWithValidPhoneNoMax,
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
  });
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
        renderRow={(row: TargetPopulationList) => (
          <LookUpTargetPopulationTableRowCommunication
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
};

export default withErrorBoundary(
  LookUpTargetPopulationTableCommunication,
  'LookUpTargetPopulationTableCommunication',
);
