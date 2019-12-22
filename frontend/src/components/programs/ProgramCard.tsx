import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { theme as themeObj } from '../../theme';
import { Grid } from '@material-ui/core';

function statusToColor(theme: typeof themeObj, status: string) {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'FINISHED':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.oragne;
  }
}

const HEX_OPACITY = Math.floor(0.15 * 0xff).toString(16);
console.log('HEX_OPACITY', HEX_OPACITY);

const useStyles = makeStyles((theme: typeof themeObj) => ({
  card: {
    height: '466px',
    width: '384px',
    marginRight: '20px',
    marginBottom: '20px',
    display: 'flex',
    flexDirection: 'row',
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
  bullet: {
    display: 'inline-block',
    margin: '0 2px',
    transform: 'scale(0.8)',
  },
  pos: {
    marginBottom: 12,
  },
  statusBar: {
    width: '4px',
    height: '100%',
    backgroundColor: ({ status }: { status: string }) =>
      statusToColor(theme, status),
  },
  label: {
    ...theme.hctTypography.label,
    textTransform: 'uppercase',
  },
  value: {
    color: '#253B46',
    fontFamily: 'Roboto',
    fontSize: '14px',
    lineHeight: '19px',
  },
  tittleBox: {
    backgroundColor: '#EEEEEE6B',
    padding: '24px',
  },
  tittle: {
    color: '#253B46',
    fontFamily: 'Roboto',
    fontSize: '20px',
    lineHeight: '26px',
  },
  statusBox: {
    color: ({ status }: { status: string }) => statusToColor(theme, status),
    backgroundColor: ({ status }: { status: string }) =>
      `${statusToColor(theme, status)}${HEX_OPACITY}`,
    borderRadius: '16px',
    fontFamily: 'Roboto',
    fontSize: '10px',
    fontWeight: 500,
    letterSpacing: '1.2px',
    lineHeight: '16px',
    padding: '3px',
    textAlign: 'center',
  },
}));
interface LabelizedFieldProps {
  value?: React.ReactNode;
  children?: React.ReactElement;
  label: string;
}

function LabelizedField({ value, children, label }: LabelizedFieldProps) {
  const classes = useStyles({ status: null });

  return (
    <div>
      <Typography className={classes.label} color='textSecondary'>
        {label}
      </Typography>
      <div>
        {children || (
          <Typography className={classes.value} color='textSecondary'>
            {value}
          </Typography>
        )}
      </div>
    </div>
  );
}

export function ProgramCard() {
  const classes = useStyles({ status: 'ACTIVE' });

  return (
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
                <div className={classes.statusBox}>ACTIVE</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={12}>
              <div className={classes.tittleBox}>
                <Typography className={classes.label} color='textSecondary'>
                  Programme
                </Typography>
                <Typography className={classes.tittle} color='textSecondary'>
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
          <Button size='medium' color='primary'>
            EDIT
          </Button>
        </CardActions>
      </div>
    </Card>
  );
}
