import { PageHeader } from '../../../components/PageHeader';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import { ProgramNode } from '../../../__generated__/graphql';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;
export interface FinishedProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
}

export function FinishedProgramDetailsPageHeader({
  program,
}: FinishedProgramDetailsPageHeaderPropTypes) {
  return (
    <PageHeader title={program.name} category='Programme Management'>
      <div>
        <ButtonContainer>
          <Button
            variant='contained'
            color='primary'
            startIcon={<OpenInNewRoundedIcon />}
          >
            OPEN IN CASHSSIST
          </Button>
        </ButtonContainer>
      </div>
    </PageHeader>
  );
}
