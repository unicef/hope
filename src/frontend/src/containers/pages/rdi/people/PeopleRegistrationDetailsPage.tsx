import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { ImportedIndividualPhotoModal } from '@components/population/ImportedIndividualPhotoModal';
import { RegistrationIndividualBioData } from '@components/rdi/details/individual/RegistrationIndividualBioData/RegistrationIndividualBioData';
import { RegistrationIndividualAdditionalRegistrationInformation } from '@components/rdi/details/individual/RegistrationIndividualAdditionalRegistrationInformation/RegistrationIndividualAdditionalRegistrationInformation';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import {
  ImportedIndividualNode,
  useAllIndividualsFlexFieldsAttributesQuery,
  useHouseholdChoiceDataQuery,
  useImportedIndividualQuery,
} from '@generated/graphql';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export const PeopleRegistrationDetailsPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const { data: flexFieldsData, loading: flexFieldsDataLoading } =
    useAllIndividualsFlexFieldsAttributesQuery();
  const { data, loading, error } = useImportedIndividualQuery({
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

  const { importedIndividual } = data;
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
      title: importedIndividual.registrationDataImport.name,
      to: '..',
    },
  ];

  return (
    <div>
      <PageHeader
        title={`${t('Individual ID')}: ${importedIndividual.importId}`}
        breadCrumbs={breadCrumbsItems}
      >
        {importedIndividual.photo ? (
          <ImportedIndividualPhotoModal
            individual={importedIndividual as ImportedIndividualNode}
          />
        ) : null}
      </PageHeader>
      <Container>
        <RegistrationIndividualBioData
          individual={importedIndividual}
          choicesData={choicesData}
        />
        <RegistrationIndividualAdditionalRegistrationInformation
          individual={importedIndividual}
          flexFieldsData={flexFieldsData}
        />
      </Container>
    </div>
  );
};
