import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Button } from '@material-ui/core';
import { PageHeader } from '../../components/PageHeader';
import { ProgramDetails } from '../../components/programs/ProgramDetails';

const useStyles = makeStyles({
  container: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
  },
});
export function ProgramDetailsPage(): React.ReactElement {
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
      </div>
    </div>
  );
}
