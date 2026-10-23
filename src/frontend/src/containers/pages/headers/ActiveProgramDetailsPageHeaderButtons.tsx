import { HeaderActions } from '@components/core/HeaderActions';
import { EditProgramMenu } from '@components/programs/EditProgram/EditProgramMenu';
import { Box } from '@mui/material';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import type { ReactElement } from 'react';
import { DuplicateProgramButtonLink } from '../../dialogs/programs/DuplicateProgramButtonLink';
import { FinishProgram } from '../../dialogs/programs/FinishProgram';

export interface ActiveProgramDetailsPageHeaderPropTypes {
  program: ProgramDetail;
  canFinish: boolean;
  canEdit: boolean;
  canDuplicate: boolean;
}
export function ActiveProgramDetailsPageHeaderButtons({
  program,
  canFinish,
  canEdit,
  canDuplicate,
}: ActiveProgramDetailsPageHeaderPropTypes): ReactElement {
  return (
    <HeaderActions>
      {canFinish && (
        <Box>
          <FinishProgram program={program} />
        </Box>
      )}
      {canEdit && (
        <Box>
          <EditProgramMenu program={program} />
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
