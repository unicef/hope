import { PageHeader } from '../../../components/PageHeader';
import { Button } from '@material-ui/core';
import styled from 'styled-components';
import EditIcon from '@material-ui/icons/EditRounded';
import { ActivateProgram } from '../../dialogs/programs/ActivateProgram';
import React from 'react';
import { DeleteProgram } from '../../dialogs/programs/DeleteProgram';
import { ProgramNode } from '../../../__generated__/graphql';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface DraftProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
}
export function DraftProgramDetailsPageHeader({
  program,
}: DraftProgramDetailsPageHeaderPropTypes) {
  return (
    <PageHeader title={program.name} category='Programme Management'>
      <div>
        <ButtonContainer>
          <DeleteProgram program={program}/>
        </ButtonContainer>
        <ButtonContainer>
          <Button variant='outlined' color='primary' startIcon={<EditIcon />}>
            EDIT PROGRAMME
          </Button>
        </ButtonContainer>
        <ButtonContainer>
          <ActivateProgram program={program} />
        </ButtonContainer>
      </div>
    </PageHeader>
  );
}
