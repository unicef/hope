import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { ImportedIndividualPhotoModal } from '../../../components/population/ImportedIndividualPhotoModal';
import { RegistrationIndividualBioData } from '../../../components/rdi/details/individual/RegistrationIndividualBioData/RegistrationIndividualBioData';
import { RegistrationIndividualVulnerabilities } from '../../../components/rdi/details/individual/RegistrationIndividualVulnerabilities/RegistrationIndividualVulnerabilities';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  ImportedIndividualNode,
  useAllIndividualsFlexFieldsAttributesQuery,
  useHouseholdChoiceDataQuery,
  useImportedIndividualQuery,
} from '../../../__generated__/graphql';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function RegistrationIndividualDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const {
    data: flexFieldsData,
    loading: flexFieldsDataLoading,
  } = useAllIndividualsFlexFieldsAttributesQuery();
  const { data, loading, error } = useImportedIndividualQuery({
    variables: {
      id,
    },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

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
            to: `/${businessArea}/registration-data-import/`,
          },
        ]
      : []),
    {
      title: importedIndividual.registrationDataImport.name,
      to: `/${businessArea}/registration-data-import/${btoa(
        `RegistrationDataImportNode:${importedIndividual.registrationDataImport.hctId}`,
      )}`,
    },
  ];

  if (importedIndividual?.household?.id) {
    breadCrumbsItems.push({
      title: `${t('HOUSEHOLD ID')}: ${importedIndividual?.household.importId}`,
      to: `/${businessArea}/registration-data-import/household/${importedIndividual?.household?.id}`,
    });
  }

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
          businessArea={businessArea}
          individual={importedIndividual}
          choicesData={choicesData}
        />
        <RegistrationIndividualVulnerabilities
          individual={importedIndividual}
          flexFieldsData={flexFieldsData}
        />
      </Container>
    </div>
  );
}
