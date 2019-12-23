import React from 'react';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { makeStyles } from '@material-ui/core/styles';
import { PageHeader } from '../../components/PageHeader';
import Container from '@material-ui/core/Container';
import { Button } from '@material-ui/core';

const useStyles = makeStyles({
  container: {
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
});
export function ProgramsPage() {
  const classes = useStyles({});
  return (
    <div>
        <PageHeader title='Programme Management' >
            <Button variant="contained" color="primary">
                NEW PROGRAMME
            </Button>
        </PageHeader>
      <Container maxWidth='lg' className={classes.container}>
        <div className={classes.container}>
          <ProgramCard />
          <ProgramCard />
          <ProgramCard />
          <ProgramCard />
        </div>
      </Container>
    </div>
  );
}
