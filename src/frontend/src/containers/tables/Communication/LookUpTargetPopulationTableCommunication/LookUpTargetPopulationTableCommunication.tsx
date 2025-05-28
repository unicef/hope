import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from './LookUpTargetPopulationTableHeadCellsCommunication';
import { LookUpTargetPopulationTableRowCommunication } from './LookUpTargetPopulationTableRowCommunication';
import { PaymentPlanStatus } from '@generated/graphql';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';
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

  const initialQueryVariables = useMemo(
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
      statusNot: PaymentPlanStatus.Open,
      isTargetPopulation: true,
      businessAreaSlug: businessArea,
      programSlug: programId,
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
