import { Grid } from '@material-ui/core';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { theme as themeObj } from '../../theme';
import { choicesToDict, programStatusToColor } from '../../utils/utils';
import {
  ProgrammeChoiceDataQuery,
  ProgramNode,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';
import { StatusBox } from '../StatusBox';
import { UniversalMoment } from '../UniversalMoment';

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
  program: ProgramNode;
  choices: ProgrammeChoiceDataQuery;
}

export function ProgramCard({
  program,
  choices,
}: ProgramCardProps): React.ReactElement {
  const { t } = useTranslation();
  const classes = useStyles({ status: program.status });
  const businessArea = useBusinessArea();
  const { programFrequencyOfPaymentsChoices, programSectorChoices } = choices;
  const programFrequencyOfPaymentsChoicesDict = choicesToDict(
    programFrequencyOfPaymentsChoices,
  );
  const programSectorChoicesDict = choicesToDict(programSectorChoices);
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
                  label={t('TIMEFRAME')}
                  value={
                    <>
                      <UniversalMoment>{program.startDate}</UniversalMoment>-
                      <UniversalMoment>{program.endDate}</UniversalMoment>
                    </>
                  }
                />
              </Grid>
              <Grid className={classes.gridElement} item xs={5}>
                <LabelizedField label={t('status')}>
                  <StatusBox
                    status={program.status}
                    statusToColor={programStatusToColor}
                  />
                </LabelizedField>
              </Grid>
              <Grid className={classes.gridElement} item xs={12}>
                <div className={classes.tittleBox}>
                  <Typography className={classes.label}>
                    {t('Programme')}
                  </Typography>
                  <Typography className={classes.tittle}>
                    {program.name}
                  </Typography>
                </div>
              </Grid>

              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField
                  label={t('Frequency of payments')}
                  value={
                    programFrequencyOfPaymentsChoicesDict[
                      program.frequencyOfPayments
                    ]
                  }
                />
              </Grid>
              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField
                  label={t('Budget (USD)')}
                  value={`${program.budget.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })} USD`}
                />
              </Grid>

              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField
                  label={t('Population Goal (# of Individuals)')}
                  value={program.populationGoal}
                />
              </Grid>
              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField
                  label={t('Num. of households')}
                  value={program.totalNumberOfHouseholds}
                />
              </Grid>

              <Grid className={classes.gridElement} item xs={6}>
                <LabelizedField
                  label={t('SECTOR')}
                  value={programSectorChoicesDict[program.sector]}
                />
              </Grid>
            </Grid>
          </CardContent>
        </div>
      </Card>{' '}
    </Link>
  );
}
