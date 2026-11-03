import { useTranslation } from 'react-i18next';
import { Overview } from '@components/payments/Overview';
import { Title } from '@core/Title';
import { Typography } from '@mui/material';
import { LabelizedField } from '@core/LabelizedField';
import { displayNameWithLatin, getPhoneNoLabel } from '@utils/utils';
import { useProgramContext } from 'src/programContext';
import type { ReactElement } from 'react';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

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
      <ResponsiveGridContainer spacing={3}>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t(`${beneficiaryGroup?.memberLabel.toUpperCase()} ID`)}
            value={individual.unicefId}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t(`${beneficiaryGroup?.memberLabel.toUpperCase()} ID`)}
            value={displayNameWithLatin(individual, 'fullName')}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('PHONE NUMBER')}
            value={getPhoneNoLabel(individual.phoneNo, individual.phoneNoValid)}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('ALT. PHONE NUMBER')}
            value={getPhoneNoLabel(
              individual.phoneNoAlternative,
              individual.phoneNoAlternativeValid,
            )}
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </Overview>
  );
};
