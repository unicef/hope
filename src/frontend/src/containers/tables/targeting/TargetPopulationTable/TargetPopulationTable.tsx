import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllTargetPopulationsQueryVariables,
  PaymentPlanNode,
  useAllTargetPopulationsQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { adjustHeadCells, dateToIsoString } from '@utils/utils';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './TargetPopulationTableHeadCells';
import { TargetPopulationTableRow } from './TargetPopulationTableRow';
import { useProgramContext } from 'src/programContext';

interface TargetPopulationProps {
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

export function TargetPopulationTable({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedTargetPopulation,
  handleChange,
  noTableStyling,
  noTitle,
}: TargetPopulationProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { businessArea, programId } = useBaseUrl();
  const initialVariables: AllTargetPopulationsQueryVariables = {
    name: filter.name,
    totalHouseholdsCountMin: filter.totalHouseholdsCountMin || null,
    totalHouseholdsCountMax: filter.totalHouseholdsCountMax || null,
    status: filter.status,
    businessArea,
    program: programId,
    createdAtRange: JSON.stringify({
      min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
      max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
    }),
  };
  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const replacements = {
    total_households_count: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalTable<PaymentPlanNode, AllTargetPopulationsQueryVariables>
        title={noTitle ? null : t('Target Populations')}
        headCells={
          enableRadioButton ? adjustedHeadCells : adjustedHeadCells.slice(1)
        }
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllTargetPopulationsQuery}
        queriedObjectName="allPaymentPlans"
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationTableRow
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
