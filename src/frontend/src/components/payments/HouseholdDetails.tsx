import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Overview } from '@components/payments/Overview';
import { Title } from '@core/Title';
import { Grid, Typography } from '@mui/material';
import { LabelizedField } from '@core/LabelizedField';
import { getPhoneNoLabel } from '@utils/utils';

export const HouseholdDetails = ({ household }): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Overview>
      <Title>
        <Typography variant="h6">{t('Household')}</Typography>
      </Title>
      <Grid container spacing={3}>
        <Grid item xs={3}>
          <LabelizedField
            label={t('HOUSEHOLD ID')}
            value={household.unicefId}
          />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('HEAD OF HOUSEHOLD')}
            value={household.headOfHousehold.fullName}
          />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('TOTAL PERSON COVERED')}
            value={household.size}
          />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('PHONE NUMBER')}
            value={getPhoneNoLabel(
              household.headOfHousehold.phoneNo,
              household.headOfHousehold.phoneNoValid,
            )}
          />
        </Grid>
        <Grid item xs={3}>
          <LabelizedField
            label={t('ALT. PHONE NUMBER')}
            value={getPhoneNoLabel(
              household.headOfHousehold.phoneNoAlternative,
              household.headOfHousehold.phoneNoAlternativeValid,
            )}
          />
        </Grid>
      </Grid>
    </Overview>
  );
};
