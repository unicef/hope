import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import { Link } from 'react-router-dom';
import moment from 'moment';
import { Grid } from '@material-ui/core';
import { theme as themeObj } from '../../theme';
import { programStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';
import { StatusBox } from '../StatusBox';
import { ProgramNode } from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const useStyles = makeStyles((theme: typeof themeObj) => ({
  card: {
    height: '466px',
    width: '384px',
    marginRight: '20px',
    marginBottom: '20px',
    display: 'flex',
    flexDirection: 'row',
  },
  aContainer: {
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
  gridElement: {
    marginBottom: theme.spacing(2),
  },
}));
interface ProgramCardProps {
  program: ProgramNode; // AllProgramsQueryResponse['allPrograms']['edges'][number]['node'];
}

export function ProgramCard({ program }: ProgramCardProps): React.ReactElement {
  const classes = useStyles({ status: program.status });
  const businessArea = useBusinessArea();
  return (
    <Link
      to={`/${businessArea}/programs/${program.id}`}
      className={classes.aContainer}
    >
      <Card className={classes.card}>
        <div className={classes.statusBar} />
        <div className={classes.container}>
          <CardContent className={classes.content}>
            <Grid container spacing={4}>
              <Grid className={classes.gridElement} item xs={7}>
                <LabelizedField
                  label='TIMEFRAME'
                  value={`${moment(program.startDate).format(
                    'DD MMM YYYY',
                  )} - ${moment(program.endDate).format('DD MMM YYYY')}`}
                />
              </Grid>
              <Grid className={classes.gridElement} item xs={5}>
                <LabelizedField label='status'>
                  <StatusBox
                    status={program.status}
                    statusToColor={programStatusToColor}
                  />
                </LabelizedField>
              </Grid>
              <Grid className={classes.gridElement} item xs={12}>
                <div className={classes.tittleBox}>
                  <Typography className={classes.label}>Programme</Typography>
                  <Typography className={classes.tittle}>
                    {program.name}
                  </Typography>
                </div>
              </Grid>

              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField label='Frequency of payments' value='Regular' />
              </Grid>
              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField
                  label='Budget'
                  value={`${program.budget.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })} USD`}
                />
              </Grid>

              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField
                  label='Population Goal'
                  value={program.populationGoal}
                />
              </Grid>
              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField
                  label='no. of households'
                  value={program.totalNumberOfHouseholds}
                />
              </Grid>

              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField label='SECTOR' value={program.sector} />
              </Grid>
            </Grid>
          </CardContent>
        </div>
      </Card>{' '}
    </Link>
  );
}
