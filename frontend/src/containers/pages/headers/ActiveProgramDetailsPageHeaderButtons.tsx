import { Button } from '@mui/material';
import styled from 'styled-components';
import OpenInNewRoundedIcon from '@mui/icons-material/OpenInNewRounded';
import React from 'react';
import {
  ProgramNode,
  useCashAssistUrlPrefixQuery,
} from '../../../__generated__/graphql';
import { FinishProgram } from '../../dialogs/programs/FinishProgram';
import { EditProgram } from '../../dialogs/programs/EditProgram';
import { LoadingComponent } from '../../../components/core/LoadingComponent';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface ActiveProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canFinish: boolean;
  canEdit: boolean;
}
export function ActiveProgramDetailsPageHeaderButtons({
  program,
  canFinish,
  canEdit,
}: ActiveProgramDetailsPageHeaderPropTypes): React.ReactElement {
  const { data, loading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <div>
      {canFinish && (
        <ButtonContainer>
          <FinishProgram program={program} />
        </ButtonContainer>
      )}
      {canEdit && (
        <ButtonContainer>
          <EditProgram program={program} />
        </ButtonContainer>
      )}
      <ButtonContainer>
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
      </ButtonContainer>
    </div>
  );
}
