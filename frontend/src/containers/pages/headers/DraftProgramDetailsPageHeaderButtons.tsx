import { Box } from '@material-ui/core';
import React from 'react';
import { ProgramQuery } from '../../../__generated__/graphql';
import { ActivateProgram } from '../../dialogs/programs/ActivateProgram';
import { DeleteProgram } from '../../dialogs/programs/DeleteProgram';
import { EditProgram } from '../../dialogs/programs/EditProgram';

export interface DraftProgramDetailsPageHeaderPropTypes {
  program: ProgramQuery['program'];
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
      {canEdit && (
        <Box m={2}>
          <EditProgram program={program} />
        </Box>
      )}
      {canRemove && (
        <Box m={2}>
          <DeleteProgram program={program} />
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
