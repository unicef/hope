import { Box } from '@material-ui/core';
import React from 'react';
import { ProgramNode } from '../../../__generated__/graphql';
import { ActivateProgram } from '../../dialogs/programs/ActivateProgram';
import { DeleteProgram } from '../../dialogs/programs/DeleteProgram';
import { EditProgram } from '../../dialogs/programs/EditProgram';

export interface DraftProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canRemove: boolean;
  canEdit: boolean;
  canActivate: boolean;
}
export const DraftProgramDetailsPageHeaderButtons = ({
  program,
  canRemove,
  canEdit,
  canActivate,
}: DraftProgramDetailsPageHeaderPropTypes): React.ReactElement => {
  return (
    <Box display='flex' alignItems='center'>
      {canRemove && (
        <Box m={2}>
          <DeleteProgram program={program} />
        </Box>
      )}
      {canEdit && (
        <Box m={2}>
          <EditProgram program={program} />
        </Box>
      )}
      {canActivate && (
        <Box m={2}>
          <ActivateProgram program={program} />
        </Box>
      )}
    </Box>
  );
};
