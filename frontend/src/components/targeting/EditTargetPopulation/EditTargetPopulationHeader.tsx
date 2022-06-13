import { Button } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { LoadingButton } from '../../core/LoadingButton';
import { PageHeader } from '../../core/PageHeader';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

interface EditTargetPopulationProps {
  handleSubmit: () => Promise<void>;
  cancelEdit: () => void;
  values;
  businessArea: string;
  targetPopulation;
  loading: boolean;
}

export function EditTargetPopulationHeader({
  handleSubmit,
  cancelEdit,
  values,
  businessArea,
  targetPopulation,
  loading,
}: EditTargetPopulationProps): React.ReactElement {
  const { t } = useTranslation();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Targeting'),
      to: `/${businessArea}/target-population/`,
    },
  ];

  const isTitleEditable = (): boolean => targetPopulation.status !== 'LOCKED';

  return (
    <PageHeader
      title={
        isTitleEditable() ? (
          <Field
            name='name'
            label={t('Enter Target Population Name')}
            type='text'
            fullWidth
            required
            component={FormikTextField}
          />
        ) : (
          values.name
        )
      }
      breadCrumbs={breadCrumbsItems}
      hasInputComponent
    >
      <>
        {values.name && (
          <ButtonContainer>
            <Button variant='outlined' color='primary' onClick={cancelEdit}>
              {t('Cancel')}
            </Button>
          </ButtonContainer>
        )}
        <ButtonContainer>
          <LoadingButton
            variant='contained'
            color='primary'
            onClick={handleSubmit}
            loading={loading}
            disabled={
              values.criterias?.length +
                values.candidateListCriterias?.length ===
                0 ||
              !values.name ||
              loading
            }
          >
            {t('Save')}
          </LoadingButton>
        </ButtonContainer>
      </>
    </PageHeader>
  );
}
