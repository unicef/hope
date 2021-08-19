import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { decodeIdString } from '../../../utils/utils';
import {
  AllTargetPopulationsQueryVariables,
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './TargetPopulationTableHeadCells';
import { TargetPopulationTableRow } from './TargetPopulationTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface TargetPopulationProps {
  filter;
  canViewDetails: boolean;
}

export const TargetPopulationTable = ({
  filter,
  canViewDetails,
}: TargetPopulationProps): ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const initialVariables: AllTargetPopulationsQueryVariables = {
    name: filter.name,
    numberOfHouseholdsMin: filter.numIndividuals.min,
    numberOfHouseholdsMax: filter.numIndividuals.max,
    status: filter.status,
    businessArea,
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
  return (
    <TableWrapper>
      <UniversalTable<TargetPopulationNode, AllTargetPopulationsQueryVariables>
        title={t('Target Populations')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllTargetPopulationsQuery}
        queriedObjectName='allTargetPopulation'
        defaultOrderBy='createdAt'
        defaultOrderDirection='desc'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationTableRow
            key={row.id}
            targetPopulation={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
