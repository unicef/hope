import { Box, Grid, Typography } from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { FlagTooltip } from '../../../components/core/FlagTooltip';
import { WarningTooltip } from '../../../components/core/WarningTooltip';
import { LabelizedField } from '../../../components/core/LabelizedField';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { HouseholdVulnerabilities } from '../../../components/population/HouseholdVulnerabilities/HouseholdVulnerabilities';
import { UniversalMoment } from '../../../components/core/UniversalMoment';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  HouseholdNode,
  useAllHouseholdsFlexFieldsAttributesQuery,
  useGrievancesChoiceDataQuery,
  useHouseholdChoiceDataQuery,
  useHouseholdQuery,
} from '../../../__generated__/graphql';
import { HouseholdCompositionTable } from '../../tables/population/HouseholdCompositionTable/HouseholdCompositionTable';
import { HouseholdIndividualsTable } from '../../tables/population/HouseholdIndividualsTable/HouseholdIndividualsTable';
import { PaymentRecordHouseholdTable } from '../../tables/payments/PaymentRecordHouseholdTable';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { HouseholdDetails } from '../../../components/population/HouseholdDetails';
import { Title } from '../../../components/core/Title';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0;
  }
`;

const SubTitle = styled(Typography)`
  && {
    font-size: 16px;
  }
`;

export function PopulationHouseholdDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { data, loading, error } = useHouseholdQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: flexFieldsData,
    loading: flexFieldsDataLoading,
  } = useAllHouseholdsFlexFieldsAttributesQuery();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();
  const {
    data: grievancesChoices,
  } = useGrievancesChoiceDataQuery();

  if (loading || choicesLoading || flexFieldsDataLoading)
    return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || !choicesData || !flexFieldsData || permissions === null)
    return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Households'),
      to: `/${businessArea}/population/household`,
    },
  ];

  const { household } = data;

  return (
    <>
      <PageHeader
        title={`${t('Household ID')}: ${household.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
        flags={
          <>
            <Box mr={2}>
              {household.hasDuplicates && (
                <WarningTooltip
                  confirmed
                  message={t('Houesehold has Duplicates')}
                />
              )}
            </Box>
            <Box mr={2}>
              {household.sanctionListPossibleMatch && (
                <FlagTooltip message={t('Sanction List Possible Match')} />
              )}
            </Box>
            <Box mr={2}>
              {household.sanctionListConfirmedMatch && (
                <FlagTooltip
                  message={t('Sanction List Confirmed Match')}
                  confirmed
                />
              )}
            </Box>
          </>
        }
      />
      <HouseholdDetails
        choicesData={choicesData}
        household={household as HouseholdNode}
        businessArea={businessArea} grievancesChoices={grievancesChoices} />
      <HouseholdCompositionTable household={household as HouseholdNode} />
      <Container>
        <HouseholdIndividualsTable
          choicesData={choicesData}
          household={household as HouseholdNode}
        />
        {hasPermissions(
          PERMISSIONS.PRORGRAMME_VIEW_LIST_AND_DETAILS,
          permissions,
        ) && (
            <PaymentRecordHouseholdTable
              openInNewTab
              household={household as HouseholdNode}
              businessArea={businessArea}
              canViewPaymentRecordDetails={hasPermissions(
                PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
                permissions,
              )}
            />
          )}
        <HouseholdVulnerabilities
          household={household as HouseholdNode}
          flexFieldsData={flexFieldsData}
        />
        <Overview>
          <Title>
            <Typography variant='h6'>{t('Registration Details')}</Typography>
          </Title>
          <Grid container spacing={6}>
            <Grid item xs={3}>
              <LabelizedField label={t('Source')}>
                <div>{household.registrationDataImport.dataSource}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Import name')}>
                <div>{household.registrationDataImport.name}</div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Registration Date')}>
                <div>
                  <UniversalMoment>
                    {household.lastRegistrationDate}
                  </UniversalMoment>
                </div>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('User name')}>
                {household.registrationDataImport.importedBy?.email}
              </LabelizedField>
            </Grid>
          </Grid>
          {household.registrationDataImport.dataSource === 'XLS' ? null : (
            <>
              <hr />
              <SubTitle variant='h6'>{t('Data Collection')}</SubTitle>
              <Grid container spacing={6}>
                <Grid item xs={3}>
                  <LabelizedField label={t('Start time')}>
                    <UniversalMoment>{household.start}</UniversalMoment>
                  </LabelizedField>
                </Grid>
                <Grid item xs={3}>
                  <LabelizedField label={t('End time')}>
                    <UniversalMoment>
                      {household.firstRegistrationDate}
                    </UniversalMoment>
                  </LabelizedField>
                </Grid>
                <Grid item xs={3}>
                  <LabelizedField label={t('Device ID')}>
                    {household.deviceid}
                  </LabelizedField>
                </Grid>
              </Grid>
            </>
          )}
        </Overview>
      </Container>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={data.household.id} />
      )}
    </>
  );
}
