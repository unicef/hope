import { useTranslation } from 'react-i18next';
import { Overview } from '@components/payments/Overview';
import { Title } from '@core/Title';
import { Grid2 as Grid, Typography } from '@mui/material';
import { LabelizedField } from '@core/LabelizedField';
import { getPhoneNoLabel } from '@utils/utils';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';

export const HouseholdDetails = ({ household }): ReactElement => {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <Overview>
      <Title>
        <Typography variant="h6">{beneficiaryGroup?.groupLabel}</Typography>
      </Title>
      <Grid container spacing={3}>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={`${beneficiaryGroup?.groupLabel} ID`}
            value={household.unicefId}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={`HEAD OF ${beneficiaryGroup?.groupLabel}`}
            value={household.headOfHousehold.fullName}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t('TOTAL PERSON COVERED')}
            value={household.size}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
          <LabelizedField
            label={t('PHONE NUMBER')}
            value={getPhoneNoLabel(
              household.headOfHousehold.phoneNo,
              household.headOfHousehold.phoneNoValid,
            )}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
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
