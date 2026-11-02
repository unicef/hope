import { HeaderActions } from '@components/core/HeaderActions';
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
    <HeaderActions>
      {canActivate && (
        <Box>
          <ReactivateProgram program={program} />
        </Box>
      )}
      {canDuplicate && (
        <Box>
          <DuplicateProgramButtonLink program={program} />
        </Box>
      )}
    </HeaderActions>
  );
}
