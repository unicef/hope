import { EditProgramMenu } from '@components/programs/EditProgram/EditProgramMenu';
import { Box } from '@mui/material';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { ReactElement } from 'react';
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
    <Box display="flex" alignItems="center">
      {canFinish && (
        <Box m={2}>
          <FinishProgram program={program} />
        </Box>
      )}
      {canEdit && (
        <Box m={2}>
          <EditProgramMenu program={program} />
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
