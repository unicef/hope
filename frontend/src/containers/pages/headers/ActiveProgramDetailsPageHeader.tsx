import { Button } from '@material-ui/core';
import styled from 'styled-components';
import EditIcon from '@material-ui/icons/EditRounded';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import React from 'react';
import { ProgramNode } from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { FinishProgram } from '../../dialogs/programs/FinishProgram';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface ActiveProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
}
export function ActiveProgramDetailsPageHeader({
  program,
}: ActiveProgramDetailsPageHeaderPropTypes) {
  return (
    <PageHeader title={program.name} category='Programme Management'>
      <div>
        <ButtonContainer>
          <FinishProgram program={program}/>
        </ButtonContainer>
        <ButtonContainer>
          <Button variant='outlined' color='primary' startIcon={<EditIcon />}>
            EDIT PROGRAMME
          </Button>
        </ButtonContainer>
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
