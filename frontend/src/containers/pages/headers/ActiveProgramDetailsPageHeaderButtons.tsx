import { Box, Button } from '@mui/material';
import OpenInNewRoundedIcon from '@mui/icons-material/OpenInNewRounded';
import React from 'react';
import {
  ProgramQuery,
  useCashAssistUrlPrefixQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { DuplicateProgramButtonLink } from '../../dialogs/programs/DuplicateProgramButtonLink';
import { EditProgramButtonLink } from '../../dialogs/programs/EditProgramButtonLink';
import { FinishProgram } from '../../dialogs/programs/FinishProgram';

export interface ActiveProgramDetailsPageHeaderPropTypes {
  program: ProgramQuery['program'];
  canFinish: boolean;
  canEdit: boolean;
  canDuplicate: boolean;
  isPaymentPlanApplicable: boolean;
}
export const ActiveProgramDetailsPageHeaderButtons = ({
  program,
  canFinish,
  canEdit,
  canDuplicate,
  isPaymentPlanApplicable,
}: ActiveProgramDetailsPageHeaderPropTypes): React.ReactElement => {
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
          <EditProgramButtonLink program={program} />
        </Box>
      )}
      {!isPaymentPlanApplicable && (
        <Box m={2}>
          <Button
            variant="contained"
            color="primary"
            component="a"
            disabled={!program.caHashId}
            target="_blank"
            href={`${data.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_program&id=${program.caHashId}`}
            startIcon={<OpenInNewRoundedIcon />}
          >
            Open in CashAssist
          </Button>
        </Box>
      )}
      {canDuplicate && (
        <Box m={2}>
          <DuplicateProgramButtonLink program={program} />
        </Box>
      )}
    </Box>
  );
};
