import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button, Typography, Paper } from '@material-ui/core';
import { Field, Form, Formik, FieldArray } from 'formik';
import { PageHeader } from '../../components/PageHeader';
import { TargetingCriteria } from '../../components/TargetPopulation/TargetingCriteria';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { Results } from '../../components/TargetPopulation/Results';
import { EditTargetPopulation } from '../../components/TargetPopulation/EditTargetPopulation';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const initialValues = {
  name: '',
  criterias: [
    {
      intakeGroup: 'Children 9/10/2019',
      sex: 'Female',
      age: '7 - 15 years old',
      distanceToSchool: 'over 3km',
      household: 'over 5 individuals',
    },
    {
      intakeGroup: 'Children 9/10/2019',
      sex: 'Male',
      age: null,
      distanceToSchool: 'over 3km',
      household: null,
    },
  ],
};

export function CreateTargetPopulation() {
  const { t } = useTranslation();

  return (
    <EditTargetPopulation />
  );
}
