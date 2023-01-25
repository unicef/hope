import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { TargetPopulationTableRow } from '../../../containers/tables/targeting/TargetPopulationTable/TargetPopulationTableRow';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { decodeIdString } from '../../../utils/utils';
import {
  AllTargetPopulationsQueryVariables,
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
} from '../../../__generated__/graphql';
import { TableWrapper } from '../../core/TableWrapper';
import { headCells } from './EnrollmentsTableHeadCells';

interface TargetPopulationProps {
  filter;
  canViewDetails: boolean;
}

export const EnrollmentsTable = ({
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
        title={t('Enrollments List')}
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
