import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Snackbar, SnackbarContent } from '@material-ui/core';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { PageHeader } from '../../components/PageHeader';
import {
  ProgramNode,
  useAllProgramsQuery,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { CreateProgram } from '../dialogs/programs/CreateProgram';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';
import { useSnackbarHelper } from '../../hooks/useBreadcrumbHelper'
import { RegistrationDataImport } from '../dialogs/registration/RegistrationDataImport';

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 20px;
  justify-content: center;
`;
export function RegistrationDataImportPage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();

  const toolbar = (
    <PageHeader title={t('Registration Data Import')}>
      <RegistrationDataImport />
    </PageHeader>
  );
  // if (loading || choicesLoading) {
  //   return <LoadingComponent />;
  // }
  // if (!data || !data.allPrograms || !choices) {
  //   return <div>{toolbar}</div>;
  // }
  return (
    <div>
      {toolbar}
    </div>
  );
}
