import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBusinessArea } from '@hooks/useBusinessArea';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './LookUpTargetPopulationTableHeadCellsCommunication';
import { LookUpTargetPopulationTableRowCommunication } from './LookUpTargetPopulationTableRowCommunication';
import {
  AllPaymentPlansForTableQueryVariables,
  PaymentPlanNode,
  PaymentPlanStatus,
  useAllPaymentPlansForTableQuery,
} from '@generated/graphql';
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
  const businessArea = useBusinessArea();
  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    businessArea,
    totalHouseholdsCountWithValidPhoneNoMin:
      filter.totalHouseholdsCountWithValidPhoneNoMin || 0,
    totalHouseholdsCountWithValidPhoneNoMax:
      filter.totalHouseholdsCountWithValidPhoneNoMax || null,
    status: [filter.status],
    createdAtRange: JSON.stringify({
      min: filter.createdAtRangeMin || null,
      max: filter.createdAtRangeMax || null,
    }),
    statusNot: PaymentPlanStatus.Open,
    isTargetPopulation: true,
  };

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalTable<PaymentPlanNode, AllPaymentPlansForTableQueryVariables>
        title={noTitle ? null : t('Target Populations')}
        headCells={enableRadioButton ? headCells : headCells.slice(1)}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllPaymentPlansForTableQuery}
        queriedObjectName="allPaymentPlans"
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        initialVariables={initialVariables}
        renderRow={(row) => (
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
