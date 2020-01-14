import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Button } from '@material-ui/core';
import { PageHeader } from '../../components/PageHeader';
import { ProgramDetails } from '../../components/programs/ProgramDetails';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { CashPlanTable } from '../CashPlanTable';
import { useQuery } from 'relay-hooks/lib';
import programQuery, {
  ProgramQuery,
} from '../../__generated__/ProgramQuery.graphql';

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
  const { props, error, retry, cached } = useQuery<ProgramQuery>(
    programQuery,
    { id },
    {},
  );
  const classes = useStyles({});
  if(!props){
    return null;
  }
  const { program } = props;
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
        <ProgramDetails program={program}/>
        <PageContainer>
          <CashPlanTable cashPlans={program.cashPlans} />
        </PageContainer>
      </div>
    </div>
  );
}
