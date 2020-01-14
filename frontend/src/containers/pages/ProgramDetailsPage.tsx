import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Button } from '@material-ui/core';
import { PageHeader } from '../../components/PageHeader';
import { ProgramDetails } from '../../components/programs/ProgramDetails';
import { TableComponent } from '../../components/table/TableComponent';
import Container from '@material-ui/core/Container';
import styled from 'styled-components';
import { CashPlanTable } from '../../components/programs/CashPlanTable';
import { useQuery } from 'relay-hooks/lib';
import { AllProgramsQuery } from '../../__generated__/AllProgramsQuery.graphql';
import { allProgramsQuery } from '../../relay/queries/allProgramsQuery';

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
  const { props, error, retry, cached } = useQuery<ProgramQuery>(
    allProgramsQuery,
    {},
    {},
  );
  const classes = useStyles({});
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
        <ProgramDetails />
        <PageContainer>
          <CashPlanTable />
        </PageContainer>
      </div>
    </div>
  );
}
