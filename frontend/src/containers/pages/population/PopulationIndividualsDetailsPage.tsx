import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { FlagTooltip } from '../../../components/core/FlagTooltip';
import { WarningTooltip } from '../../../components/core/WarningTooltip';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { IndividualBioData } from '../../../components/population/IndividualBioData/IndividualBioData';
import { IndividualPhotoModal } from '../../../components/population/IndividualPhotoModal';
import { IndividualVulnerabilities } from '../../../components/population/IndividualVulnerabilities/IndividualVunerabilities';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  IndividualNode,
  useHouseholdChoiceDataQuery,
  useIndividualQuery,
  useAllIndividualsFlexFieldsAttributesQuery,
  useGrievancesChoiceDataQuery,
} from '../../../__generated__/graphql';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function PopulationIndividualsDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { data, loading, error } = useIndividualQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  const {
    data: flexFieldsData,
    loading: flexFieldsDataLoading,
  } = useAllIndividualsFlexFieldsAttributesQuery();

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
      title: 'Individuals',
      to: `/${businessArea}/population/individuals`,
    },
  ];

  const { individual } = data;

  let duplicateTooltip = null;
  if (individual.status === 'DUPLICATE') {
    duplicateTooltip = (
      <WarningTooltip confirmed message={t('Confirmed Duplicate')} />
    );
  } else if (individual.deduplicationGoldenRecordStatus !== 'UNIQUE') {
    duplicateTooltip = <WarningTooltip message={t('Possible Duplicate')} />;
  }

  return (
    <div>
      <PageHeader
        title={`${t('Individual ID')}: ${individual.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
        flags={
          <>
            <Box mr={2}>{duplicateTooltip}</Box>
            <Box mr={2}>
              {individual.sanctionListPossibleMatch && (
                <FlagTooltip message={t('Sanction List Possible Match')} />
              )}
            </Box>
            <Box mr={2}>
              {individual.sanctionListConfirmedMatch && (
                <FlagTooltip
                  message={t('Sanction List Confirmed Match')}
                  confirmed
                />
              )}
            </Box>
          </>
        }
      >
        <Box mr={2}>
          {individual.photo ? (
            <IndividualPhotoModal individual={individual as IndividualNode} />
          ) : null}
        </Box>
      </PageHeader>

      <Container>
        <IndividualBioData
          businessArea={businessArea}
          individual={individual as IndividualNode}
          choicesData={choicesData} grievancesChoices={grievancesChoices} />
        <IndividualVulnerabilities
          flexFieldsData={flexFieldsData}
          individual={individual as IndividualNode}
        />
        {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTable objectId={individual.id} />
        )}
      </Container>
    </div>
  );
}
