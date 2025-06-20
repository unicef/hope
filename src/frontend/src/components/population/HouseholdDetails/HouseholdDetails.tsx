import { Box, Grid2 as Grid, Theme, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useProgramContext } from '../../../programContext';
import { formatCurrencyWithSymbol } from '@utils/utils';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import {
  BigValue,
  BigValueContainer,
} from '../../rdi/details/RegistrationDetails/RegistrationDetails';
import { LinkedGrievancesModal } from '../LinkedGrievancesModal/LinkedGrievancesModal';
import { ReactElement } from 'react';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { Overview } from '@components/payments/Overview';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';

const Container = styled.div<{ theme?: Theme }>`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
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
      <Container>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={`${beneficiaryGroup?.groupLabel} Size`}>
              {household?.size}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Residence Status')}>
              {household?.residenceStatus}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 6 }}>
            <LabelizedField label={`Head of ${beneficiaryGroup?.groupLabel}`}>
              <ContentLink
                href={`/${baseUrl}/population/individuals/${household?.headOfHousehold?.id}`}
              >
                {household?.headOfHousehold?.fullName}
              </ContentLink>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('FEMALE CHILD HEADED ' + beneficiaryGroup?.groupLabel)}
            >
              {household?.fchildHoh ? t('Yes') : t('No')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('CHILD HEADED ' + beneficiaryGroup?.groupLabel)}
            >
              {household?.childHoh ? t('Yes') : t('No')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Country')}>
              {household?.country}
            </LabelizedField>
          </Grid>
        </Grid>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={`${beneficiaryGroup?.groupLabel} Size`}>
              {household?.size}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Residence Status')}>
              {household?.residenceStatus}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 6 }}>
            <LabelizedField label={`Head of ${beneficiaryGroup?.groupLabel}`}>
              <ContentLink
                href={`/${baseUrl}/population/individuals/${household?.headOfHousehold?.id}`}
              >
                {household?.headOfHousehold?.fullName}
              </ContentLink>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('FEMALE CHILD HEADED ' + beneficiaryGroup?.groupLabel)}
            >
              {household?.fchildHoh ? t('Yes') : t('No')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('CHILD HEADED ' + beneficiaryGroup?.groupLabel)}
            >
              {household?.childHoh ? t('Yes') : t('No')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Country')}>
              {household?.country}
            </LabelizedField>
          </Grid>
        </Grid>
        <Grid container spacing={3}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={`${beneficiaryGroup?.groupLabel} Size`}>
              {household?.size}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Residence Status')}>
              {household?.residenceStatus}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 6 }}>
            <LabelizedField label={`Head of ${beneficiaryGroup?.groupLabel}`}>
              <ContentLink
                href={`/${baseUrl}/population/individuals/${household?.headOfHousehold?.id}`}
              >
                {household?.headOfHousehold?.fullName}
              </ContentLink>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('FEMALE CHILD HEADED ' + beneficiaryGroup?.groupLabel)}
            >
              {household?.fchildHoh ? t('Yes') : t('No')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('CHILD HEADED ' + beneficiaryGroup?.groupLabel)}
            >
              {household?.childHoh ? t('Yes') : t('No')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Country')}>
              {household?.country}
            </LabelizedField>
          </Grid>

          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Country of Origin')}>
              {household?.countryOrigin}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Address')}>
              {household?.address}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Village')}>
              {household?.village}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Zip code')}>
              {household?.zipCode}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Administrative Level 1')}>
              {household?.admin1?.name}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Administrative Level 2')}>
              {household?.admin2?.name}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Administrative Level 3')}>
              {household?.admin3?.name}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Administrative Level 4')}>
              {household?.admin4?.name}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 6 }}>
            <LabelizedField label={t('Geolocation')}>
              {household?.geopoint
                ? `${household?.geopoint?.[0]}, ${household?.geopoint?.[1]}`
                : '-'}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('UNHCR CASE ID')}>
              {household?.unhcrId}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('LENGTH OF TIME SINCE ARRIVAL')}>
              {household?.flexFields?.months_displaced_h_f}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('NUMBER OF TIMES DISPLACED')}>
              {household?.flexFields?.number_times_displaced_h_f}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t(
                'IS THIS A RETURNEE ' + beneficiaryGroup?.groupLabel + '?',
              )}
            >
              {household?.returnee ? t('Yes') : t('No')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            {household?.unicefId && (
              <LinkedGrievancesModal
                household={household}
                baseUrl={baseUrl}
                businessArea={businessArea}
                grievancesChoices={grievancesChoices}
              />
            )}
          </Grid>
          <Grid size={{ xs: 3 }}>
            {household?.unicefId && (
              <LinkedGrievancesModal
                household={household}
                baseUrl={baseUrl}
                businessArea={businessArea}
                grievancesChoices={grievancesChoices}
              />
            )}
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Data Collecting Type')}>
              {selectedProgram?.dataCollectingType?.label}
            </LabelizedField>
          </Grid>
        </Grid>
      </Container>
      <Overview>
        <Title>
          <Typography variant="h6">{t('Benefits')}</Typography>
        </Title>
        <Grid container>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Cash received')}>
              {household?.deliveredQuantities?.length ? (
                <Box mb={2}>
                  <Grid container>
                    <Grid size={{ xs: 6 }}>
                      <Box display="flex" flexDirection="column">
                        {household?.deliveredQuantities?.map((item) => (
                          <Box
                            key={`${item.currency}-${item.totalDeliveredQuantity}`}
                          >
                            {item.currency === 'USD'
                              ? formatCurrencyWithSymbol(
                                  item.totalDeliveredQuantity,
                                  item.currency,
                                )
                              : `(${formatCurrencyWithSymbol(
                                  item.totalDeliveredQuantity,
                                  item.currency,
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
          </Grid>
          <Grid size={{ xs: 3 }}>
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
          </Grid>
        </Grid>
      </Overview>
    </>
  );
}
