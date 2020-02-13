import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { ProgramNode } from '../../../__generated__/graphql';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;
export interface FinishedProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
}

export function FinishedProgramDetailsPageHeaderButtons({
  program,
}: FinishedProgramDetailsPageHeaderPropTypes): React.ReactElement {
  return (
    <div>
      <ButtonContainer>
        <Button
          variant='contained'
          color='primary'
          component='a'
          href={`/cashassist/${program.programCaId}`}
          startIcon={<OpenInNewRoundedIcon />}
        >
          OPEN IN CASHSSIST
        </Button>
      </ButtonContainer>
    </div>
  );
}
