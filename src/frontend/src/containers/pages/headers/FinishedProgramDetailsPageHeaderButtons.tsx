import { Box } from '@mui/material';
import { DuplicateProgramButtonLink } from '../../dialogs/programs/DuplicateProgramButtonLink';
import { ReactivateProgram } from '../../dialogs/programs/ReactivateProgram';
import type { ReactElement } from 'react';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';

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
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}
    >
      {canActivate && (
        <Box
          sx={{
            m: 2,
          }}
        >
          <ReactivateProgram program={program} />
        </Box>
      )}
      {canDuplicate && (
        <Box
          sx={{
            m: 2,
          }}
        >
          <DuplicateProgramButtonLink program={program} />
        </Box>
      )}
    </Box>
  );
}
