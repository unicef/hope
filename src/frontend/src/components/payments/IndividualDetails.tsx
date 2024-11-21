import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Overview } from '@components/payments/Overview';
import { Title } from '@core/Title';
import { Grid, Typography } from '@mui/material';
import { LabelizedField } from '@core/LabelizedField';
import { getPhoneNoLabel } from '@utils/utils';
import { useProgramContext } from 'src/programContext';

export const IndividualDetails = ({ individual }): React.ReactElement => {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <Overview>
      <Title>
        <Typography variant="h6">
          {t(`${beneficiaryGroup?.memberLabel}`)}
        </Typography>{' '}
      </Title>
      <Grid container spacing={3}>
        <Grid item xs={3}>
          <LabelizedField
            label={t(`${beneficiaryGroup?.memberLabel.toUpperCase()} ID`)}
            value={individual.unicefId}
          />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t(`${beneficiaryGroup?.memberLabel.toUpperCase()} ID`)}
            value={individual.fullName}
          />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('PHONE NUMBER')}
            value={getPhoneNoLabel(individual.phoneNo, individual.phoneNoValid)}
          />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('ALT. PHONE NUMBER')}
            value={getPhoneNoLabel(
              individual.phoneNoAlternative,
              individual.phoneNoAlternativeValid,
            )}
          />
        </Grid>
      </Grid>
    </Overview>
  );
};
