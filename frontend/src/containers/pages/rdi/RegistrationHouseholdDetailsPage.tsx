import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { HouseholdDetails } from '../../../components/rdi/details/households/HouseholdDetails/HouseholdDetails';
import { RegistrationDetails } from '../../../components/rdi/details/households/RegistrationDetails';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  useHouseholdChoiceDataQuery,
  useImportedHouseholdQuery,
} from '../../../__generated__/graphql';
import { HouseholdImportedIndividualsTable } from '../../tables/rdi/HouseholdImportedIndividualsTable/HouseholdImportedIndividualsTable';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function RegistrationHouseholdDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { data, loading, error } = useImportedHouseholdQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  if (loading || choicesLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || !choicesData || permissions === null) return null;

  const { importedHousehold } = data;
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
      title: importedHousehold.registrationDataImport.name,
      to: `/${businessArea}/registration-data-import/${btoa(
        `RegistrationDataImportNode:${importedHousehold.registrationDataImport.hctId}`,
      )}`,
    },
  ];

  return (
    <div>
      <PageHeader
        title={`${'Household ID'}: ${importedHousehold.importId}`}
        breadCrumbs={breadCrumbsItems}
      />
      <HouseholdDetails
        businessArea={businessArea}
        choicesData={choicesData}
        household={importedHousehold}
      />
      <Container>
        <HouseholdImportedIndividualsTable
          choicesData={choicesData}
          household={importedHousehold}
        />
        <RegistrationDetails
          hctId={importedHousehold.registrationDataImport.hctId}
          registrationDate={importedHousehold.firstRegistrationDate}
          deviceid={importedHousehold.deviceid}
          start={importedHousehold.start}
          koboAssetId={importedHousehold.koboAssetId}
          rowId={importedHousehold.rowId}
        />
      </Container>
    </div>
  );
}
