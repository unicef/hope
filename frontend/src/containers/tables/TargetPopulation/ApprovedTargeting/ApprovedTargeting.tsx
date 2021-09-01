import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useCandidateHouseholdsListByTargetingCriteriaQuery } from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells as programmeHeadCells } from '../SentTargeting/ProgrammeHeadCells';
import { ProgrammeTableRow } from '../SentTargeting/ProgrammeTableRow';

const TableWrapper = styled.div`
  padding: 20px;
  position: relative;
`;

interface TargetPopulationHouseholdProps {
  id?: string;
  variables?;
  canViewDetails?: boolean;
}

export const ApprovedTargetPopulationTable = ({
  id,
  variables,
  canViewDetails,
}: TargetPopulationHouseholdProps): ReactElement => {
  const { t } = useTranslation();
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables,
  };
  return (
    <TableWrapper>
      <UniversalTable
        title={t('Households')}
        headCells={programmeHeadCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useCandidateHouseholdsListByTargetingCriteriaQuery}
        queriedObjectName='candidateHouseholdsListByTargetingCriteria'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <ProgrammeTableRow household={row} canViewDetails={canViewDetails} />
        )}
      />
    </TableWrapper>
  );
};
