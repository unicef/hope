import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBusinessArea } from '@hooks/useBusinessArea';
import { decodeIdString } from '@utils/utils';
import {
  AllActiveTargetPopulationsQueryVariables,
  AllPaymentPlansForTableQuery,
  AllPaymentPlansForTableQueryVariables,
  PaymentPlanNode,
  TargetPopulationNode,
  TargetPopulationStatus,
  useAllActiveTargetPopulationsQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './LookUpTargetPopulationTableHeadCellsCommunication';
import { LookUpTargetPopulationTableRowCommunication } from './LookUpTargetPopulationTableRowCommunication';

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

export const LookUpTargetPopulationTableCommunication = ({
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
    totalHouseholdsCountWithValidPhoneNoMin:
      filter.totalHouseholdsCountWithValidPhoneNoMin || 0,
    totalHouseholdsCountWithValidPhoneNoMax:
      filter.totalHouseholdsCountWithValidPhoneNoMax || null,
    status: filter.status,
    businessArea,
    //TODO: createdAtRange missing?
    createdAtRange: JSON.stringify({
      min: filter.createdAtRangeMin || null,
      max: filter.createdAtRangeMax || null,
    }),
    //TODO: statusNot add this filter?
    statusNot: TargetPopulationStatus.Open,
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
        query={useAllActiveTargetPopulationsQuery}
        queriedObjectName="allActiveTargetPopulations"
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
