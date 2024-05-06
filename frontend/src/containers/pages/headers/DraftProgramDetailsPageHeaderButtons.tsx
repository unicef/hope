import { Box } from '@mui/material';
import * as React from 'react';
import { ProgramQuery } from '@generated/graphql';
import { ActivateProgram } from '../../dialogs/programs/ActivateProgram';
import { DeleteProgram } from '../../dialogs/programs/DeleteProgram';
import { DuplicateProgramButtonLink } from '../../dialogs/programs/DuplicateProgramButtonLink';
import { EditProgramButtonLink } from '../../dialogs/programs/EditProgramButtonLink';

export interface DraftProgramDetailsPageHeaderPropTypes {
  program: ProgramQuery['program'];
  canRemove: boolean;
  canEdit: boolean;
  canActivate: boolean;
  canDuplicate: boolean;
}
export function DraftProgramDetailsPageHeaderButtons({
  program,
  canRemove,
  canEdit,
  canActivate,
  canDuplicate,
}: DraftProgramDetailsPageHeaderPropTypes): React.ReactElement {
  return (
    <Box display="flex" alignItems="center">
      {canRemove && (
        <Box m={2}>
          <DeleteProgram program={program} />
        </Box>
      )}
      {canEdit && (
        <Box m={2}>
          <EditProgramButtonLink program={program} />
        </Box>
      )}
      {canActivate && (
        <Box m={2}>
          <ActivateProgram program={program} />
        </Box>
      )}
      {canDuplicate && (
        <Box m={2}>
          <DuplicateProgramButtonLink program={program} />
        </Box>
      )}
    </Box>
  );
}
