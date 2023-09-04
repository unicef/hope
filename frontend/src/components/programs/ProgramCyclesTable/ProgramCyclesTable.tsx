import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  ProgramNode,
  ProgramStatus,
  useAllGrievanceTicketQuery,
  useProgrammeChoiceDataQuery,
} from '../../../__generated__/graphql';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { AddNewProgramCycle } from '../../../containers/dialogs/programs/programCycles/AddNewProgramCycle/AddNewProgramCycle';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { choicesToDict } from '../../../utils/utils';
import { LoadingComponent } from '../../core/LoadingComponent';
import { TableWrapper } from '../../core/TableWrapper';
import { headCells } from './ProgramCyclesTableHeadCells';
import { ProgramCyclesTableRow } from './ProgramCyclesTableRow';

interface ProgramCyclesTableProps {
  filter?;
  program: ProgramNode;
}

const Subtitle = styled(Box)`
  color: #7c8990;
  text-align: center;
  font-size: 24px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
`;

export const ProgramCyclesTable = ({
  program,
}: ProgramCyclesTableProps): React.ReactElement => {
  const loading = false;
  const { data } = useProgrammeChoiceDataQuery();
  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();

  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
  };

  const permissions = usePermissions();

  if (!permissions) {
    return null;
  }

  if (loading) {
    return <LoadingComponent />;
  }
  const subtitle = (
    <Subtitle p={18}>{t('Activate the programme to create a cycle')}</Subtitle>
  );

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(data.programStatusChoices);

  const isProgramActive = program.status === ProgramStatus.Active;

  const canViewProgramCycleDetails = hasPermissions(
    PERMISSIONS.PROGRAMME_CYCLE_VIEW_DETAILS,
    permissions,
  );

  const canEditProgramCycle = hasPermissions(
    PERMISSIONS.PROGRAMME_CYCLE_UPDATE,
    permissions,
  );
  const canDeleteProgramCycle = hasPermissions(
    PERMISSIONS.PROGRAMME_CYCLE_REMOVE,
    permissions,
  );

  const addNewProgramCycleButton = [<AddNewProgramCycle program={program} />];

  //TODO: connect ProgrammeCycle query

  return (
    <TableWrapper>
      <UniversalTable<
        AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
        AllGrievanceTicketQueryVariables
      >
        headCells={headCells}
        title={t('Programme Cycles')}
        rowsPerPageOptions={[10, 15, 20, 40]}
        query={useAllGrievanceTicketQuery}
        queriedObjectName='allGrievanceTicket'
        initialVariables={initialVariables}
        defaultOrderBy='created_at'
        defaultOrderDirection='desc'
        renderRow={(row) => (
          <ProgramCyclesTableRow
            key={row.id}
            programCycle={row}
            statusChoices={statusChoices}
            canViewProgramCycleDetails={canViewProgramCycleDetails}
            canEditProgramCycle={canEditProgramCycle}
            canDeleteProgramCycle={canDeleteProgramCycle}
          />
        )}
        componentInsteadOfRows={!isProgramActive ? subtitle : null}
        actions={addNewProgramCycleButton}
      />
    </TableWrapper>
  );
};
