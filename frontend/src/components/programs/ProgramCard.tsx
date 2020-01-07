import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { theme as themeObj } from '../../theme';
import { Grid } from '@material-ui/core';
import { programStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';
import { StatusBox } from '../StatusBox';

const useStyles = makeStyles((theme: typeof themeObj) => ({
  card: {
    height: '466px',
    width: '384px',
    marginRight: '20px',
    marginBottom: '20px',
    display: 'flex',
    flexDirection: 'row',
  },
  aContainer:{
    textDecoration: 'none',
  },
  container: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    flex: 1,
    padding: '24px',
  },
  content: {
    display: 'flex',
    flexDirection: 'column',
    padding: 0,
  },
  actions: {
    padding: 0,
    justifyContent: 'flex-end',
  },
  statusBar: {
    width: '4px',
    height: '100%',
    backgroundColor: ({ status }: { status: string }) =>
      programStatusToColor(theme, status),
  },
  label: {
    ...theme.hctTypography.label,
    textTransform: 'uppercase',
  },
  tittleBox: {
    backgroundColor: '#EEEEEE6B',
    padding: '24px',
  },
  tittle: {
    color: '#253B46',
    ...theme.hctTypography.font,
    fontSize: '20px',
    lineHeight: '26px',
  },
}));

export function ProgramCard() {
  const classes = useStyles({ status: 'ACTIVE' });

  return (
    <a href='/programs/1' className={classes.aContainer}>
      <Card className={classes.card}>
        <div className={classes.statusBar} />
        <div className={classes.container}>
          <CardContent className={classes.content}>
            <Grid container spacing={3}>
              <Grid item xs={7}>
                <LabelizedField
                  label='TIMEFRAME'
                  value='01 Jan 2019 - 31 Dec 2020'
                />
              </Grid>
              <Grid item xs={5}>
                <LabelizedField label='status'>
                  <StatusBox
                    status='ACTIVE'
                    statusToColor={programStatusToColor}
                  />
                </LabelizedField>
              </Grid>
              <Grid item xs={12}>
                <div className={classes.tittleBox}>
                  <Typography className={classes.label}>
                    Programme
                  </Typography>
                  <Typography className={classes.tittle}>
                    Helping young children in remote locations
                  </Typography>
                </div>
              </Grid>

              <Grid item xs={6}>
                <LabelizedField label='Frequency of payments' value='Regular' />
              </Grid>
              <Grid item xs={6}>
                <LabelizedField label='Budget' value='2,500,000.00 USD' />
              </Grid>

              <Grid item xs={6}>
                <LabelizedField label='Population Goal' value='25,000' />
              </Grid>
              <Grid item xs={6}>
                <LabelizedField label='no. of households' value='-' />
              </Grid>

              <Grid item xs={6}>
                <LabelizedField label='SECTOR' value='Nutricion' />
              </Grid>
            </Grid>
          </CardContent>
          <CardActions className={classes.actions}>
            <Button size='medium' color='primary' component="a" href="/programs/1/edit">
              EDIT
            </Button>
          </CardActions>
        </div>
      </Card>{' '}
    </a>
  );
}
