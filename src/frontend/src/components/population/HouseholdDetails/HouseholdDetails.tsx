import { Overview } from '@components/payments/Overview';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { Box, Grid, Typography } from '@mui/material';
import type { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import type { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { displayNameWithLatin, formatCurrencyWithSymbol } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  SECTION_PADDING,
} from 'src/responsive';
import styled from 'styled-components';
import { useProgramContext } from '../../../programContext';
import {
  BigValue,
  BigValueContainer,
} from '../../rdi/details/RegistrationDetails/RegistrationDetails';
import { LinkedGrievancesModal } from '../LinkedGrievancesModal/LinkedGrievancesModal';

const Container = styled(Box)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  flex-direction: column;
  align-items: center;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;

  && > div {
    margin: 5px;
  }
`;

interface HouseholdDetailsProps {
  household: HouseholdDetail;
  baseUrl: string;
  businessArea: string;
  grievancesChoices: GrievanceChoices;
}
export function HouseholdDetails({
  household,
  baseUrl,
  businessArea,
  grievancesChoices,
}: HouseholdDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <>
      <Container sx={{ padding: SECTION_PADDING }}>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <ResponsiveGridContainer spacing={3}>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={`${beneficiaryGroup?.groupLabel} Size`}>
              {household?.kabSize ?? '-'}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Residence Status')}>
              {household?.residenceStatus}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="half">
            <LabelizedField label={`Head of ${beneficiaryGroup?.groupLabel}`}>
              <ContentLink
                href={`/${baseUrl}/population/individuals/${household?.headOfHousehold?.id}`}
              >
                {displayNameWithLatin(household?.headOfHousehold, 'fullName')}
              </ContentLink>
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('FEMALE CHILD HEADED ' + beneficiaryGroup?.groupLabel)}
            >
              {household?.fchildHoh ? t('Yes') : t('No')}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t('CHILD HEADED ' + beneficiaryGroup?.groupLabel)}
            >
              {household?.childHoh ? t('Yes') : t('No')}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Country')}>
              {household?.country}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Country of Origin')}>
              {household?.countryOrigin}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Address')}>
              {household?.address}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Village')}>
              {household?.village}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Zip code')}>
              {household?.zipCode}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Administrative Level 1')}>
              {household?.admin1?.name}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Administrative Level 2')}>
              {household?.admin2?.name}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Administrative Level 3')}>
              {household?.admin3?.name}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Administrative Level 4')}>
              {household?.admin4?.name}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="half">
            <LabelizedField label={t('Geolocation')}>
              {household?.geopoint
                ? `${household?.geopoint?.[0]}, ${household?.geopoint?.[1]}`
                : '-'}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('UNHCR CASE ID')}>
              {household?.unhcrId}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Facility Name')}>
              {household?.facilityName}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('LENGTH OF TIME SINCE ARRIVAL')}>
              {household?.flexFields?.months_displaced_h_f}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('NUMBER OF TIMES DISPLACED')}>
              {household?.flexFields?.number_times_displaced_h_f}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField
              label={t(
                'IS THIS A RETURNEE ' + beneficiaryGroup?.groupLabel + '?',
              )}
            >
              {household?.returnee ? t('Yes') : t('No')}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            {household?.unicefId && (
              <LinkedGrievancesModal
                household={household}
                baseUrl={baseUrl}
                businessArea={businessArea}
                grievancesChoices={grievancesChoices}
              />
            )}
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Data Collecting Type')}>
              {selectedProgram?.dataCollectingType?.label}
            </LabelizedField>
          </ResponsiveGrid>
        </ResponsiveGridContainer>
      </Container>
      <Overview>
        <Title>
          <Typography variant="h6">{t('Benefits')}</Typography>
        </Title>
        <Grid container>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <LabelizedField label={t('Cash received')}>
              {household?.deliveredQuantities?.length ? (
                <Box
                  sx={{
                    mb: 2,
                  }}
                >
                  <Grid container>
                    <Grid size={6}>
                      <Box
                        sx={{
                          display: 'flex',
                          flexDirection: 'column',
                        }}
                      >
                        {household?.deliveredQuantities?.map((item) => (
                          <Box key={item.currencyVisionCode}>
                            {item.currency === 'USD'
                              ? formatCurrencyWithSymbol(
                                  item.totalDeliveredQuantity,
                                  item.currency,
                                )
                              : `(${formatCurrencyWithSymbol(
                                  item.totalDeliveredQuantity,
                                  item.currency,
                                  item.currencyVisionCode,
                                )})`}
                          </Box>
                        ))}
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              ) : (
                <>-</>
              )}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" mobileSize="half">
            <BigValueContainer>
              <LabelizedField label={t('Total Cash Received')}>
                <BigValue>
                  {formatCurrencyWithSymbol(
                    Number(household?.totalCashReceivedUsd),
                    'USD',
                  )}
                </BigValue>
              </LabelizedField>
            </BigValueContainer>
          </ResponsiveGrid>
        </Grid>
      </Overview>
    </>
  );
}
