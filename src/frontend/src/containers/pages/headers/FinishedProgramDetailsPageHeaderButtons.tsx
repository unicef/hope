import { Box } from '@mui/material';
import { ProgramQuery, useCashAssistUrlPrefixQuery } from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { DuplicateProgramButtonLink } from '../../dialogs/programs/DuplicateProgramButtonLink';
import { ReactivateProgram } from '../../dialogs/programs/ReactivateProgram';
import { ReactElement } from 'react';

export interface FinishedProgramDetailsPageHeaderPropTypes {
  program: ProgramQuery['program'];
  canActivate: boolean;
  canDuplicate: boolean;
}

export function FinishedProgramDetailsPageHeaderButtons({
  program,
  canActivate,
  canDuplicate,
}: FinishedProgramDetailsPageHeaderPropTypes): ReactElement {
  const { data, loading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
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
