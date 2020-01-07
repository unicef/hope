import React from 'react';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { makeStyles } from '@material-ui/core/styles';
import { PageHeader } from '../../components/PageHeader';
import Container from '@material-ui/core/Container';
import { Button } from '@material-ui/core';
import { ProgramDetails } from '../../components/programs/ProgramDetails';

const useStyles = makeStyles({
  container: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
  },
});
export function ProgramDetailsPage() {
  const classes = useStyles({});
  return (
    <div>
      <PageHeader title='DETAILS'>
        <Button variant='contained' color='primary'>
          EDIT
        </Button>
      </PageHeader>
      <div className={classes.container}>
        <ProgramDetails />
      </div>
    </div>
  );
}
