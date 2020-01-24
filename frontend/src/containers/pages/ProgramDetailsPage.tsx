import React from 'react';
import { Button } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { ProgramDetails } from '../../components/programs/ProgramDetails';
import { CashPlanTable } from '../CashPlanTable';
import {
  ProgramNode,
  ProgramStatus,
  useProgramQuery,
} from '../../__generated__/graphql';
import CloseIcon from '@material-ui/icons/CloseRounded';
import EditIcon from '@material-ui/icons/EditRounded';
import { ActivateProgram } from '../Dialogs/Programme/ActivateProgramme';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
`;
const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;
const RemoveButton = styled(Button)`
  && {
    color: ${({ theme }) => theme.palette.error.main};
  }
`;

export function ProgramDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data } = useProgramQuery({
    variables: { id },
  });
  if (!data) {
    return null;
  }
  const program = data.program as ProgramNode;
  return (
    <div>
      <PageHeader
        title={program.name}
        category='Programme Management'
      >
        <div>
          <ButtonContainer>
            <RemoveButton startIcon={<CloseIcon />}>REMOVE</RemoveButton>
          </ButtonContainer>
          <ButtonContainer>
            <Button variant='outlined' color='primary' startIcon={<EditIcon />}>
              EDIT PROGRAMME
            </Button>
          </ButtonContainer>
          {program.status === ProgramStatus.Draft ? (
            <ButtonContainer>
              <ActivateProgram program={program}/>
            </ButtonContainer>
          ) : null}
        </div>
      </PageHeader>
      <Container>
        <ProgramDetails program={program} />
        <PageContainer>
          <CashPlanTable program={program} />
        </PageContainer>
      </Container>
    </div>
  );
}
