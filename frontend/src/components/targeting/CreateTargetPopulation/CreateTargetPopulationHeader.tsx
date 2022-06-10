import { Button } from '@mui/material';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

interface CreateTargetPopulationHeaderProps {
  handleSubmit: () => Promise<void>;
  values;
  businessArea: string;
  permissions: string[];
}

export function CreateTargetPopulationHeader({
  handleSubmit,
  values,
  businessArea,
  permissions,
}: CreateTargetPopulationHeaderProps): React.ReactElement {
  const { t } = useTranslation();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Targeting'),
      to: `/${businessArea}/target-population/`,
    },
  ];

  return (
    <PageHeader
      title={
        <Field
          name='name'
          label={t('Enter Target Population Name')}
          type='text'
          fullWidth
          required
          component={FormikTextField}
        />
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
      hasInputComponent
    >
      <>
        <ButtonContainer>
          <Button
            variant='contained'
            color='primary'
            onClick={handleSubmit}
            disabled={values.criterias?.length === 0 || !values.name}
            data-cy='button-target-population-create'
          >
            {t('Save')}
          </Button>
        </ButtonContainer>
      </>
    </PageHeader>
  );
}
