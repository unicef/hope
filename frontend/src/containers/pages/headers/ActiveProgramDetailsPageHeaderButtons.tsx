import { Box, Button } from '@material-ui/core';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import {
  ProgramNode,
  useCashAssistUrlPrefixQuery,
} from '../../../__generated__/graphql';
import { FinishProgram } from '../../dialogs/programs/FinishProgram';
import { EditProgram } from '../../dialogs/programs/EditProgram';
import { LoadingComponent } from '../../../components/core/LoadingComponent';

export interface ActiveProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canFinish: boolean;
  canEdit: boolean;
}
export const ActiveProgramDetailsPageHeaderButtons = ({
  program,
  canFinish,
  canEdit,
}: ActiveProgramDetailsPageHeaderPropTypes): React.ReactElement => {
  const { data, loading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <Box display='flex' alignItems='center'>
      {canFinish && (
        <Box m={2}>
          <FinishProgram program={program} />
        </Box>
      )}
      {canEdit && (
        <Box m={2}>
          <EditProgram program={program} />
        </Box>
      )}
      <Box m={2}>
        <Button
          variant='contained'
          color='primary'
          component='a'
          disabled={!program.caHashId}
          target='_blank'
          href={`${data.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_program&id=${program.caHashId}`}
          startIcon={<OpenInNewRoundedIcon />}
        >
          Open in CashAssist
        </Button>
      </Box>
    </Box>
  );
};
