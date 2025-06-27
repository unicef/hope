import { LoadingComponent } from '@components/core/LoadingComponent';
import { EditProgramMenu } from '@components/programs/EditProgram/EditProgramMenu';
import { ProgramQuery, useCashAssistUrlPrefixQuery } from '@generated/graphql';
import { Box } from '@mui/material';
import { DuplicateProgramButtonLink } from '../../dialogs/programs/DuplicateProgramButtonLink';
import { FinishProgram } from '../../dialogs/programs/FinishProgram';
import { ReactElement } from 'react';

export interface ActiveProgramDetailsPageHeaderPropTypes {
  program: ProgramQuery['program'];
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
  const { data, loading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
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
