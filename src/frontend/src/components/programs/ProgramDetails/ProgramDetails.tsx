import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import {
  choicesToDict,
  isPartnerVisible,
  programStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { MiśTheme } from 'src/theme';
import styled from 'styled-components';
import { PartnerAccess } from '../constants';

const NumberOfHouseHolds = styled.div`
  padding: ${({ theme }) => theme.spacing(8)};
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;
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
      <Grid container spacing={6}>
        {Object.keys(counts).map((level) => (
          <Grid size={{ xs: 3 }} key={level}>
            <LabelizedField
              dataCy={`admin-area-${level}-total-count`}
              label={t(`Admin Area ${level}`)}
            >
              {counts[level]}
            </LabelizedField>
          </Grid>
        ))}
      </Grid>
    );
  };

  let partners = [];
  partners = program.partners.filter((partner) =>
    isPartnerVisible(partner.name),
  );

  const showPartners = partners.length > 0;
  return (
    <ContainerColumnWithBorder data-cy="program-details-container">
      <Title>
        <Typography variant="h6">{t('Programme Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid size={{ xs: 4 }}>
            <LabelizedField label={t('status')}>
              <StatusBox
                status={program.status}
                statusToColor={programStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('START DATE')}
              value={<UniversalMoment>{program.startDate}</UniversalMoment>}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('END DATE')}
              value={<UniversalMoment>{program.endDate}</UniversalMoment>}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Programme Code')}
              value={program.programmeCode}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Sector')}
              value={programSectorChoicesDict[program.sector]}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Data Collecting Type')}
              value={program?.dataCollectingType?.label}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Beneficiary Group')}
              value={program?.beneficiaryGroup?.name}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Frequency of Payment')}
              value={
                programFrequencyOfPaymentsChoicesDict[
                  program.frequencyOfPayments
                ]
              }
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Administrative Areas of implementation')}
              value={program.administrativeAreasOfImplementation}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Description')}
              value={program.description}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('CASH+')}
              value={program.cashPlus ? t('Yes') : t('No')}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              label={t('Partner Access')}
              value={PartnerAccess[program.partnerAccess]}
            />
          </Grid>
        </Grid>
        <NumberOfHouseHolds>
          <LabelizedField label={t('Programme size')}>
            <NumberOfHouseHoldsValue>
              {program.householdCount}
            </NumberOfHouseHoldsValue>
          </LabelizedField>
        </NumberOfHouseHolds>
      </OverviewContainer>
      {showPartners && (
        <>
          <DividerLine />
          <Title>
            <Typography variant="h6">{t('Programme Partners')}</Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              {partners.map((partner) => (
                <Grid key={partner.id} size={{ xs: 12 }}>
                  <StyledBox p={6} flexDirection="column">
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
                </Grid>
              ))}
            </Grid>
          </OverviewContainer>
        </>
      )}
    </ContainerColumnWithBorder>
  );
};
