import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import { Grid, Typography } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import { HouseholdDetails } from './HouseholdDetails';
import { PageHeader } from '../../../../components/PageHeader';
import {
  CashPlanNode,
  HouseholdNode,
  useHouseholdQuery,
  useImportedHouseholdQuery,
} from '../../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { HouseholdVulnerabilities } from '../../../../components/population/HouseholdVulnerabilities';
import { LabelizedField } from '../../../../components/LabelizedField';
import { PaymentRecordTable } from '../../../tables/PaymentRecordTable';
import { HouseholdIndividualsTable } from '../../../tables/HouseholdIndividualsTable';
import { decodeIdString } from '../../../../utils/utils';
import { ImportedIndividualsTable } from '../../tables/ImportedIndividualsTable';
import { RegistrationDetails } from './RegistrationDetails';
import moment from 'moment';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0px;
  }
`;
const Content = styled.div`
  margin-top: 20px;
`;

export function RegistrationHouseholdDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const { data, loading } = useImportedHouseholdQuery({
    variables: { id },
  });

  if (loading) return null;

  const { importedHousehold } = data;
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Registration Data import',
      to: `/${businessArea}/registration-data-import/`,
    },
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
      <HouseholdDetails household={importedHousehold} />
      <Container>
        <ImportedIndividualsTable
          household={importedHousehold.id}
          isOnPaper
          rowsPerPageOptions={[5, 10, 15]}
          title='Individuals in Household'
        />
        <RegistrationDetails
          hctId={importedHousehold.registrationDataImport.hctId}
          registrationDate={moment(importedHousehold.registrationDate).format(
            'DD MMM YYYY',
          )}
        />
      </Container>
    </div>
  );
}
