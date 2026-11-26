import { useTranslation } from 'react-i18next';
import { Overview } from '@components/payments/Overview';
import { Title } from '@core/Title';
import { Typography } from '@mui/material';
import { LabelizedField } from '@core/LabelizedField';
import { getPhoneNoLabel, formatFigure } from '@utils/utils';
import { useProgramContext } from 'src/programContext';
import type { ReactElement } from 'react';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

export const HouseholdDetails = ({ household }): ReactElement => {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <Overview>
      <Title>
        <Typography variant="h6">{beneficiaryGroup?.groupLabel}</Typography>
      </Title>
      <ResponsiveGridContainer spacing={3}>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={`${beneficiaryGroup?.groupLabel} ID`}
            value={household.unicefId}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={`HEAD OF ${beneficiaryGroup?.groupLabel}`}
            value={household.headOfHousehold.fullName}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('TOTAL PERSON COVERED')}
            value={formatFigure(household.size)}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('PHONE NUMBER')}
            value={getPhoneNoLabel(
              household.headOfHousehold.phoneNo,
              household.headOfHousehold.phoneNoValid,
            )}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField
            label={t('ALT. PHONE NUMBER')}
            value={getPhoneNoLabel(
              household.headOfHousehold.phoneNoAlternative,
              household.headOfHousehold.phoneNoAlternativeValid,
            )}
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </Overview>
  );
};
