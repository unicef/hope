import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { RegistrationIndividualAdditionalRegistrationInformation } from '@components/rdi/details/individual/RegistrationIndividualAdditionalRegistrationInformation/RegistrationIndividualAdditionalRegistrationInformation';
import { RegistrationIndividualBioData } from '@components/rdi/details/individual/RegistrationIndividualBioData/RegistrationIndividualBioData';
import { AllIndividualsFlexFieldsAttributesQuery } from '@generated/graphql';
import { FieldsAttributesService } from '@restgenerated/services/FieldsAttributesService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';

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
  const { businessArea, programId } = useBaseUrl();

  const {
    data: flexFieldsData,
    isLoading: flexFieldsDataLoading,
    error,
  } = useQuery<AllIndividualsFlexFieldsAttributesQuery>({
    queryKey: ['fieldsAttributes'],
    queryFn: async () => {
      const data = await FieldsAttributesService.fieldsAttributesRetrieve();
      return { allIndividualsFlexFieldsAttributes: data };
    },
  });
  const { data: individual, isLoading: loadingIndividual } =
    useQuery<IndividualDetail>({
      queryKey: ['businessAreaProgramIndividual', businessArea, programId, id],
      queryFn: () =>
        RestService.restBusinessAreasProgramsIndividualsRetrieve({
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: id,
        }),
    });

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  if (loadingIndividual || choicesLoading || flexFieldsDataLoading)
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!individual || !choicesData || !flexFieldsData || permissions === null)
    return null;

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
        {/* //TODO: add individual photo */}
        {/* {individual.photo ? (
          <IndividualPhotoModal individual={individual} />
        ) : null} */}
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
