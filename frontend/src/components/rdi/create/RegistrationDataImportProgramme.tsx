import {Box, InputLabel, FormControl} from '@material-ui/core';
import { Field } from 'formik';
import get from 'lodash/get';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { AllProgramsForChoicesQuery } from '../../../__generated__/graphql';
import { LoadingComponent } from '../../core/LoadingComponent';
import { FormikSelectFieldConfirmProgram } from '../../targeting/FormikSelectFieldConfirmProgram';


const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(3)}px;
`;
const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;

const StyledInputLabel = styled(InputLabel)`
  background-color: #fff;
`;

export function RegistrationDataImportProgramme({
  allPrograms,
  loading,
  program,
  setFieldValue,
  values,
}: {
  allPrograms: AllProgramsForChoicesQuery;
  loading: boolean;
  program: string;
  setFieldValue;
  values;
}): React.ReactElement {
  const { t } = useTranslation();
  if (loading) return <LoadingComponent />;

  const allProgramsEdges = get(allPrograms, 'allPrograms.edges', []);
  const mappedPrograms = allProgramsEdges.map((edge) => ({
    name: edge.node.name,
    value: edge.node.id,
    individualDataNeeded: edge.node.individualDataNeeded,
  }));

  return (
    <FormControl variant='outlined' margin='dense'>
      <StyledInputLabel>{t('Select Programme')}</StyledInputLabel>
      <Box display='flex' flexDirection='column'>
        <Field
          name='program'
          label={t('Programme')}
          data-cy="input-program"
          fullWidth
          variant='outlined'
          required
          choices={mappedPrograms}
          component={FormikSelectFieldConfirmProgram}
          allProgramsEdges={allProgramsEdges}
          program={program}
          setFieldValue={setFieldValue}
          values={values}
        />
      </Box>
    </FormControl>
  );
}
