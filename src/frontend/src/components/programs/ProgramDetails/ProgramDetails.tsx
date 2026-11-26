import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { Box, Chip, Typography } from '@mui/material';
import type { PaymentPlanPurpose } from '@restgenerated/models/PaymentPlanPurpose';
import type { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import {
  choicesToDict,
  isPartnerVisible,
  programStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  responsiveValue,
} from 'src/responsive';
import type { MiśTheme } from 'src/theme';
import styled from 'styled-components';
import { PartnerAccess } from '../constants';

const NumberOfHouseHoldsValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)};
`;

const StyledBox = styled(Box)`
  border: 1px solid #e3e3e3;
`;

interface ProgramDetailsProps {
  program: ProgramDetail;
  choices: ProgramChoices;
}

export const ProgramDetails = ({
  program,
  choices,
}: ProgramDetailsProps): ReactElement => {
  const { t } = useTranslation();
  const { frequencyOfPaymentsChoices, sectorChoices } = choices;
  const programFrequencyOfPaymentsChoicesDict = choicesToDict(
    frequencyOfPaymentsChoices,
  );
  const programSectorChoicesDict = choicesToDict(sectorChoices);
  const renderAdminAreasCount = (
    partner: ProgramDetail['partners'][0],
  ): ReactElement => {
    const counts = {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
    };
    partner.areas?.forEach(({ level }) => {
      const currentCount = counts[level + 1] || 0;
      counts[level + 1] = currentCount + 1;
    });

    return (
      <ResponsiveGridContainer spacing={6}>
        {Object.keys(counts).map((level) => (
          <ResponsiveGrid size="quarter" mobileSize="half" key={level}>
            <LabelizedField
              dataCy={`admin-area-${level}-total-count`}
              label={t(`Admin Area ${level}`)}
            >
              {counts[level]}
            </LabelizedField>
          </ResponsiveGrid>
        ))}
      </ResponsiveGridContainer>
    );
  };

  const partners = program.partners.filter((partner) =>
    isPartnerVisible(partner.name),
  );

  const showPartners = partners.length > 0;
  return (
    <ContainerColumnWithBorder data-cy="program-details-container">
      <Title>
        <Typography variant="h6">{t('Programme Details')}</Typography>
      </Title>
      <OverviewContainer>
        <ResponsiveGridContainer spacing={6}>
          <ResponsiveGrid size="third">
            <LabelizedField label={t('status')}>
              <StatusBox
                status={program.status}
                statusToColor={programStatusToColor}
              />
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('START DATE')}
              value={<UniversalMoment>{program.startDate}</UniversalMoment>}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('END DATE')}
              value={<UniversalMoment>{program.endDate}</UniversalMoment>}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField label={t('Programme Code')} value={program.code} />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Sector')}
              value={programSectorChoicesDict[program.sector]}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Payee Type')}
              value={program?.payeeType?.name}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('GL Code')}
              value={program?.payeeType?.glCode}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Data Collecting Type')}
              value={program?.dataCollectingType?.label}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Payee Label')}
              value={program?.beneficiaryGroup?.name}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Frequency of Payment')}
              value={
                programFrequencyOfPaymentsChoicesDict[
                  program.frequencyOfPayments
                ]
              }
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Administrative Areas of implementation')}
              value={program.administrativeAreasOfImplementation}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Description')}
              value={program.description}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('CASH+')}
              value={program.cashPlus ? t('Yes') : t('No')}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Partner Access')}
              value={PartnerAccess[program.partnerAccess ?? '']}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Reconciliation Window (in days)')}
              value={program.reconciliationWindowInDays}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third">
            <LabelizedField
              label={t('Send reconciliation window expiry notifications')}
              value={
                program.sendReconciliationWindowExpiryNotifications
                  ? t('Yes')
                  : t('No')
              }
            />
          </ResponsiveGrid>
          {program.paymentPlanPurposes?.length > 0 && (
            <ResponsiveGrid size="full">
              <LabelizedField label={t('Payment Plan Purposes')}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {program.paymentPlanPurposes.map(
                    (purpose: PaymentPlanPurpose) => (
                      <Chip
                        key={purpose.id}
                        label={purpose.name}
                        size="small"
                      />
                    ),
                  )}
                </Box>
              </LabelizedField>
            </ResponsiveGrid>
          )}
        </ResponsiveGridContainer>
        <Box
          sx={{
            borderColor: '#b1b1b5',
            borderStyle: 'solid',
            borderWidth: responsiveValue('1px 0 0 0', '0 0 0 1px'),
            mt: responsiveValue(6, 0),
            pt: responsiveValue(4, 8),
            px: responsiveValue(0, 8),
            pb: responsiveValue(0, 8),
          }}
        >
          <LabelizedField label={t('Programme size')}>
            <NumberOfHouseHoldsValue>
              {program.householdCount}
            </NumberOfHouseHoldsValue>
          </LabelizedField>
        </Box>
      </OverviewContainer>
      {showPartners && (
        <>
          <DividerLine />
          <Title>
            <Typography variant="h6">{t('Programme Partners')}</Typography>
          </Title>
          <OverviewContainer>
            <ResponsiveGridContainer spacing={6}>
              {partners.map((partner) => (
                <ResponsiveGrid key={partner.id} size="full">
                  <StyledBox
                    sx={{
                      p: 6,
                      flexDirection: 'column',
                    }}
                  >
                    <Typography data-cy="label-partner-name" variant="h6">
                      {partner.name}
                    </Typography>
                    {partner.areaAccess === 'BUSINESS_AREA' ? (
                      <LabelizedField
                        dataCy="area-access-field"
                        label={t('Area Access')}
                      >
                        {t('Business Area')}
                      </LabelizedField>
                    ) : (
                      renderAdminAreasCount(partner)
                    )}
                  </StyledBox>
                </ResponsiveGrid>
              ))}
            </ResponsiveGridContainer>
          </OverviewContainer>
        </>
      )}
    </ContainerColumnWithBorder>
  );
};
