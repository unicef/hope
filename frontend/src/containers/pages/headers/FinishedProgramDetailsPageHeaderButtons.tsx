import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import styled from 'styled-components';
import {Button} from '@material-ui/core';
import {ReactivateProgram} from '../../dialogs/programs/ReactivateProgram';
import {ProgramNode, useCashAssistUrlPrefixQuery,} from '../../../__generated__/graphql';
import {LoadingComponent} from '../../../components/LoadingComponent';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;
export interface FinishedProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canActivate: boolean;
}

export function FinishedProgramDetailsPageHeaderButtons({
  program,
  canActivate,
}: FinishedProgramDetailsPageHeaderPropTypes): React.ReactElement {
  const { data, loading } = useCashAssistUrlPrefixQuery();
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <div>
      {canActivate && (
        <ButtonContainer>
          <ReactivateProgram program={program} />
        </ButtonContainer>
      )}
      <ButtonContainer>
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
      </ButtonContainer>
    </div>
  );
}
