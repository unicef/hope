import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../../components/BreadCrumbs';
import { LoadingComponent } from '../../../../components/LoadingComponent';
import { PageHeader } from '../../../../components/PageHeader';
import { PermissionDenied } from '../../../../components/PermissionDenied';
import { ImportedIndividualPhotoModal } from '../../../../components/population/ImportedIndividualPhotoModal';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import {
  decodeIdString,
  isPermissionDeniedError,
} from '../../../../utils/utils';
import {
  ImportedIndividualNode,
  useImportedIndividualQuery,
} from '../../../../__generated__/graphql';
import { RegistrationIndividualsBioData } from './RegistrationIndividualBioData';
import { RegistrationIndividualVulnerabilities } from './RegistrationIndividualVulnerabilities';

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
  const { data, loading, error } = useImportedIndividualQuery({
    variables: {
      id,
    },
  });

  if (loading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || permissions === null) return null;

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
      title: `${t('HOUSEHOLD ID')}: ${decodeIdString(
        importedIndividual?.household?.id,
      )}`,
      to: `/${businessArea}/registration-data-import/household/${importedIndividual?.household?.id}`,
    });
  }

  return (
    <div>
      <PageHeader
        title={`${t('Individual ID')}: ${decodeIdString(id)}`}
        breadCrumbs={breadCrumbsItems}
      >
        {importedIndividual.photo ? (
          <ImportedIndividualPhotoModal
            individual={importedIndividual as ImportedIndividualNode}
          />
        ) : null}
      </PageHeader>
      <Container>
        <RegistrationIndividualsBioData individual={importedIndividual} />
        <RegistrationIndividualVulnerabilities
          individual={importedIndividual}
        />
      </Container>
    </div>
  );
}
