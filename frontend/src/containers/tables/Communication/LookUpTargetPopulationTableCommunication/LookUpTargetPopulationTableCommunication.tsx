import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBusinessArea } from '@hooks/useBusinessArea';
import { decodeIdString } from '@utils/utils';
import {
  AllActiveTargetPopulationsQueryVariables,
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

export function LookUpTargetPopulationTableCommunication({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedTargetPopulation,
  handleChange,
  noTableStyling,
  noTitle,
}: LookUpTargetPopulationTableCommunicationProps): ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const initialVariables: AllActiveTargetPopulationsQueryVariables = {
    name: filter.name,
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
    statusNot: TargetPopulationStatus.Open,
  };

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  if (filter.program) {
    if (Array.isArray(filter.program)) {
      initialVariables.program = filter.program.map((programId) =>
        decodeIdString(programId),
      );
    } else {
      initialVariables.program = [decodeIdString(filter.program)];
    }
  }

  const renderTable = (): React.ReactElement => (
    <TableWrapper>
      <UniversalTable<
        TargetPopulationNode,
        AllActiveTargetPopulationsQueryVariables
      >
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
}
