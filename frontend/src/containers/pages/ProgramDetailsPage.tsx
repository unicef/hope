import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Button } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { ProgramDetails } from '../../components/programs/ProgramDetails';
import { CashPlanTable } from '../CashPlanTable';
import { ProgramNode, useProgramQuery } from '../../__generated__/graphql';

const useStyles = makeStyles({
  container: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
  },
});

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
`;

export function ProgramDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const { data } = useProgramQuery({
    variables: { id },
  });
  const classes = useStyles({});
  if (!data) {
    return null;
  }
  const program = data.program as ProgramNode;
  return (
    <div>
      <PageHeader
        title='Helping young children in remote locations'
        category='Programme Management'
      >
        <Button variant='contained' color='primary'>
          EDIT
        </Button>
      </PageHeader>
      <div className={classes.container}>
        <ProgramDetails program={program} />
        <PageContainer>
          <CashPlanTable program={program} />
        </PageContainer>
      </div>
    </div>
  );
}
