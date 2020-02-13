import styled from 'styled-components';
import React from 'react';
import { ActivateProgram } from '../../dialogs/programs/ActivateProgram';
import { DeleteProgram } from '../../dialogs/programs/DeleteProgram';
import { ProgramNode } from '../../../__generated__/graphql';
import { EditProgram } from '../../dialogs/programs/EditProgram';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface DraftProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
}
export function DraftProgramDetailsPageHeaderButtons({
  program,
}: DraftProgramDetailsPageHeaderPropTypes): React.ReactElement {
  return (
    <div>
      <ButtonContainer>
        <DeleteProgram program={program} />
      </ButtonContainer>
      <ButtonContainer>
        <EditProgram program={program} />
      </ButtonContainer>
      <ButtonContainer>
        <ActivateProgram program={program} />
      </ButtonContainer>
    </div>
  );
}
