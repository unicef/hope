import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Box, Button } from '@material-ui/core';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  ProgramNode,
  ProgramStatus,
  ProgrammeChoiceDataQuery,
  useAllGrievanceTicketQuery,
  useProgrammeChoiceDataQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { LoadingComponent } from '../../core/LoadingComponent';
import { TableWrapper } from '../../core/TableWrapper';
import { ProgramCyclesTableRow } from './ProgramCyclesTableRow';
import { headCells } from './ProgramCyclesTableHeadCells';
import { choicesToDict } from '../../../utils/utils';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { Add } from '@material-ui/icons';
import { AddNewProgramCycle } from '../../../containers/dialogs/programs/AddNewProgramCycle';

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
  const canRemoveProgramCycle = hasPermissions(
    PERMISSIONS.PROGRAMME_CYCLE_REMOVE,
    permissions,
  );

  const addNewProgramCycleButton = [<AddNewProgramCycle program={program} />];

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
            row={row}
            statusChoices={statusChoices}
            canViewProgramCycleDetails={canViewProgramCycleDetails}
            canEditProgramCycle={canEditProgramCycle}
            canRemoveProgramCycle={canRemoveProgramCycle}
          />
        )}
        componentInsteadOfRows={!isProgramActive ? subtitle : null}
        actions={addNewProgramCycleButton}
      />
    </TableWrapper>
  );
};
