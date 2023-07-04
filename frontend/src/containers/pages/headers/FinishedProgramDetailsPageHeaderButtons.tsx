import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import { Box, Button } from '@material-ui/core';
import { ReactivateProgram } from '../../dialogs/programs/ReactivateProgram';
import {
  ProgramNode,
  useCashAssistUrlPrefixQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { DuplicateProgram } from '../../dialogs/programs/DuplicateProgram';

export interface FinishedProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canActivate: boolean;
  canDuplicate: boolean;
}

export const FinishedProgramDetailsPageHeaderButtons = ({
  program,
  canActivate,
  canDuplicate,
}: FinishedProgramDetailsPageHeaderPropTypes): React.ReactElement => {
  const { data, loading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <Box display='flex' alignItems='center'>
      {canActivate && (
        <Box m={2}>
          <ReactivateProgram program={program} />
        </Box>
      )}
      <Box m={2}>
        <Button
          variant='contained'
          color='primary'
          component='a'
          disabled={!program.caHashId}
          href={`${data.cashAssistUrlPrefix}/&pagetype=entityrecord&etn=progres_program&id=/${program.caHashId}`}
          startIcon={<OpenInNewRoundedIcon />}
        >
          Open in CashAssist
        </Button>
      </Box>
      {/* //TODO: add when duplicate is ready
      {canDuplicate && (
        <Box m={2}>
          <DuplicateProgram programId={program.id} />
        </Box>
      )} */}
    </Box>
  );
};
