import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { IndividualPhotoModal } from '@components/population/IndividualPhotoModal';
import { RegistrationIndividualBioData } from '@components/rdi/details/individual/RegistrationIndividualBioData/RegistrationIndividualBioData';
import { RegistrationIndividualAdditionalRegistrationInformation } from '@components/rdi/details/individual/RegistrationIndividualAdditionalRegistrationInformation/RegistrationIndividualAdditionalRegistrationInformation';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import {
  IndividualNode,
  useAllIndividualsFlexFieldsAttributesQuery,
  useHouseholdChoiceDataQuery,
  useIndividualQuery,
} from '@generated/graphql';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const PeopleRegistrationDetailsPage = (): ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();

  const { data: flexFieldsData, loading: flexFieldsDataLoading } =
    useAllIndividualsFlexFieldsAttributesQuery();
  const { data, loading, error } = useIndividualQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });
  const { data: choicesData, loading: choicesLoading } =
    useHouseholdChoiceDataQuery();

  if (loading || choicesLoading || flexFieldsDataLoading)
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !choicesData || !flexFieldsData || permissions === null)
    return null;

  const { individual } = data;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    ...(hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions)
      ? [
          {
            title: t('Registration Data import'),
            to: '../..',
          },
        ]
      : []),
    {
      title: individual.registrationDataImport.name,
      to: '..',
    },
  ];

  return (
    <>
      <PageHeader
        title={`${t('Individual ID')}: ${individual.importId}`}
        breadCrumbs={breadCrumbsItems}
      >
        {individual.photo ? (
          <IndividualPhotoModal individual={individual as IndividualNode} />
        ) : null}
      </PageHeader>
      <Container>
        <RegistrationIndividualBioData
          individual={individual}
          choicesData={choicesData}
        />
        <RegistrationIndividualAdditionalRegistrationInformation
          individual={individual}
          flexFieldsData={flexFieldsData}
        />
      </Container>
    </>
  );
};
export default withErrorBoundary(
  PeopleRegistrationDetailsPage,
  'PeopleRegistrationDetailsPage',
);
