import { useTranslation } from 'react-i18next';
import { Overview } from '@components/payments/Overview';
import { Title } from '@core/Title';
import { Grid2 as Grid, Typography } from '@mui/material';
import { LabelizedField } from '@core/LabelizedField';
import { getPhoneNoLabel } from '@utils/utils';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';

export const IndividualDetails = ({ individual }): ReactElement => {
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
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t(`${beneficiaryGroup?.memberLabel.toUpperCase()} ID`)}
            value={individual.unicefId}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t(`${beneficiaryGroup?.memberLabel.toUpperCase()} ID`)}
            value={individual.fullName}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t('PHONE NUMBER')}
            value={getPhoneNoLabel(individual.phoneNo, individual.phoneNoValid)}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
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
