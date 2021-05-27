import React from 'react';
import styled from 'styled-components';
import {useParams} from 'react-router-dom';
import {PageHeader} from '../../../../components/PageHeader';
import {useHouseholdChoiceDataQuery, useImportedHouseholdQuery,} from '../../../../__generated__/graphql';
import {BreadCrumbsItem} from '../../../../components/BreadCrumbs';
import {useBusinessArea} from '../../../../hooks/useBusinessArea';
import {decodeIdString, isPermissionDeniedError,} from '../../../../utils/utils';
import {usePermissions} from '../../../../hooks/usePermissions';
import {LoadingComponent} from '../../../../components/LoadingComponent';
import {hasPermissions, PERMISSIONS} from '../../../../config/permissions';
import {PermissionDenied} from '../../../../components/PermissionDenied';
import {HouseholdImportedIndividualsTable} from "../../tables/HouseholdIndividualsTable";
import {HouseholdDetails} from './HouseholdDetails';
import {RegistrationDetails} from './RegistrationDetails';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

export function RegistrationHouseholdDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { data, loading, error } = useImportedHouseholdQuery({
    variables: { id },
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
            title: 'Registration Data import',
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
        title={`Household ID: ${decodeIdString(id)}`}
        breadCrumbs={breadCrumbsItems}
      />
      <HouseholdDetails
        choicesData={choicesData}
        household={importedHousehold}
      />
      <Container>
        <HouseholdImportedIndividualsTable
          household={importedHousehold}
        />
        <RegistrationDetails
          hctId={importedHousehold.registrationDataImport.hctId}
          registrationDate={importedHousehold.firstRegistrationDate}
          deviceid={importedHousehold.deviceid}
          start={importedHousehold.start}
        />
      </Container>
    </div>
  );
}
