import styled from 'styled-components';
import React from 'react';
import {ActivateProgram} from '../../dialogs/programs/ActivateProgram';
import {DeleteProgram} from '../../dialogs/programs/DeleteProgram';
import {ProgramNode} from '../../../__generated__/graphql';
import {EditProgram} from '../../dialogs/programs/EditProgram';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface DraftProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canRemove: boolean;
  canEdit: boolean;
  canActivate: boolean;
}
export function DraftProgramDetailsPageHeaderButtons({
  program,
  canRemove,
  canEdit,
  canActivate,
}: DraftProgramDetailsPageHeaderPropTypes): React.ReactElement {
  return (
    <div>
      {canRemove && (
        <ButtonContainer>
          <DeleteProgram program={program} />
        </ButtonContainer>
      )}
      {canEdit && (
        <ButtonContainer>
          <EditProgram program={program} />
        </ButtonContainer>
      )}
      {canActivate && (
        <ButtonContainer>
          <ActivateProgram program={program} />
        </ButtonContainer>
      )}
    </div>
  );
}
