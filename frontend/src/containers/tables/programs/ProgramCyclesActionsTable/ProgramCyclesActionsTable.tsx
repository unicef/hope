import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllProgramCyclesQuery,
  AllProgramCyclesQueryVariables,
  ProgramQuery,
  ProgramStatus,
  useAllProgramCyclesQuery,
  useProgrammeChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { AddNewProgramCycle } from '../../../dialogs/programs/programCycles/AddNewProgramCycle/AddNewProgramCycle';
import { UniversalTable } from '../../UniversalTable';
import { usePermissions } from '../../../../hooks/usePermissions';
import { choicesToDict } from '../../../../utils/utils';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import { headCells } from './ProgramCyclesActionsTableHeadCells';
import { ProgramCyclesActionsTableRow } from './ProgramCyclesActionsTableRow';

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

interface ProgramCyclesActionsTableProps {
  filter?;
  program: ProgramQuery['program'];
}

export const ProgramCyclesActionsTable = ({
  program,
}: ProgramCyclesActionsTableProps): React.ReactElement => {
  const { data: programChoiceData, loading } = useProgrammeChoiceDataQuery();
  const { t } = useTranslation();

  const initialVariables: AllProgramCyclesQueryVariables = {};

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
  } = choicesToDict(programChoiceData.programCycleStatusChoices);

  const isProgramActive = program.status === ProgramStatus.Active;

  const canViewProgramCycleDetails = hasPermissions(
    PERMISSIONS.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
    permissions,
  );

  const canEditProgramCycle = hasPermissions(
    PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE,
    permissions,
  );
  const canDeleteProgramCycle = hasPermissions(
    PERMISSIONS.PM_PROGRAMME_CYCLE_REMOVE,
    permissions,
  );

  const addNewProgramCycleButton = [
    <AddNewProgramCycle key='add-new' program={program} />,
  ];

  return (
    <TableWrapper>
      <UniversalTable<
        AllProgramCyclesQuery['allProgramCycles']['edges'][number]['node'],
        AllProgramCyclesQueryVariables
      >
        key={program.cycles?.edges?.length}
        headCells={headCells}
        title={t('Programme Cycles')}
        rowsPerPageOptions={[10, 15, 20, 40]}
        query={useAllProgramCyclesQuery}
        queriedObjectName='allProgramCycles'
        initialVariables={initialVariables}
        defaultOrderBy='created_at'
        defaultOrderDirection='desc'
        renderRow={(row) => (
          <ProgramCyclesActionsTableRow
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
