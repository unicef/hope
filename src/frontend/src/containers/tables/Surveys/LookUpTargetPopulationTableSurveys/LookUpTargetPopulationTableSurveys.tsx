import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './LookUpTargetPopulationTableHeadCellsSurveys';
import { LookUpTargetPopulationTableRowSurveys } from './LookUpTargetPopulationTableRowSurveys';
import {
  AllPaymentPlansForTableQueryVariables,
  PaymentPlanNode,
  PaymentPlanStatus,
  useAllPaymentPlansForTableQuery,
} from '@generated/graphql';

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
  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    totalHouseholdsCountWithValidPhoneNoMin:
      filter.totalHouseholdsCountMin || 0,
    totalHouseholdsCountWithValidPhoneNoMax:
      filter.totalHouseholdsCountMax || null,
    status: filter.status,
    businessArea,
    program: programId,
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
