import { Box } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  IndividualNode,
  useAllIndividualsFlexFieldsAttributesQuery,
  useGrievancesChoiceDataQuery,
  useHouseholdChoiceDataQuery,
  useIndividualQuery,
} from '../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { IndividualBioData } from '../../../components/population/IndividualBioData/IndividualBioData';
import { IndividualFlags } from '../../../components/population/IndividualFlags';
import { IndividualPhotoModal } from '../../../components/population/IndividualPhotoModal';
import { IndividualVulnerabilities } from '../../../components/population/IndividualVulnerabilities/IndividualVunerabilities';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
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
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();

  const { data, loading, error } = useIndividualQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });

  const { data: choicesData, loading: choicesLoading } = useHouseholdChoiceDataQuery();

  const { data: flexFieldsData, loading: flexFieldsDataLoading } = useAllIndividualsFlexFieldsAttributesQuery();

  const { data: grievancesChoices, loading: grievancesChoicesLoading } = useGrievancesChoiceDataQuery();

  if (
    loading
    || choicesLoading
    || flexFieldsDataLoading
    || grievancesChoicesLoading
  ) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (
    !data
    || !choicesData
    || !flexFieldsData
    || !grievancesChoices
    || permissions === null
  ) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Individuals',
      to: `/${baseUrl}/population/individuals`,
    },
  ];

  const { individual } = data;

  return (
    <>
      <PageHeader
        title={`${t('Individual ID')}: ${individual?.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
        flags={<IndividualFlags individual={individual} />}
      >
        <Box mr={2}>
          {individual?.photo ? (
            <IndividualPhotoModal individual={individual as IndividualNode} />
          ) : null}
        </Box>
      </PageHeader>

      <Container>
        <IndividualBioData
          baseUrl={baseUrl}
          businessArea={businessArea}
          individual={individual as IndividualNode}
          choicesData={choicesData}
          grievancesChoices={grievancesChoices}
        />
        <IndividualVulnerabilities
          flexFieldsData={flexFieldsData}
          individual={individual as IndividualNode}
        />
        {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTable objectId={individual?.id} />
        )}
      </Container>
    </>
  );
}
