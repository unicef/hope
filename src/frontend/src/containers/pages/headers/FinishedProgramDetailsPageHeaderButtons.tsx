import { Box } from '@mui/material';
import { DuplicateProgramButtonLink } from '../../dialogs/programs/DuplicateProgramButtonLink';
import { ReactivateProgram } from '../../dialogs/programs/ReactivateProgram';
import { ReactElement } from 'react';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';

export interface FinishedProgramDetailsPageHeaderPropTypes {
  program: ProgramDetail;
  canActivate: boolean;
  canDuplicate: boolean;
}

export function FinishedProgramDetailsPageHeaderButtons({
  program,
  canActivate,
  canDuplicate,
}: FinishedProgramDetailsPageHeaderPropTypes): ReactElement {
  return (
    <Box display="flex" alignItems="center">
      {canActivate && (
        <Box m={2}>
          <ReactivateProgram program={program} />
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
