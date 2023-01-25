import { Typography } from '@material-ui/core';
import { FieldArray, Form, Formik } from 'formik';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useCachedImportedIndividualFieldsQuery } from '../../../hooks/useCachedImportedIndividualFields';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import {
  associatedWith,
  handleValidationErrors,
  isNot,
} from '../../../utils/utils';
import {
  TargetPopulationQuery,
  TargetPopulationStatus,
  useUpdateTpMutation,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../core/LoadingComponent';
import { UniversalCriteriaPaperComponent } from '../../core/UniversalCriteriaComponent/UniversalCriteriaPaperComponent';
import { Exclusions } from '../../targeting/CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../../targeting/PaperContainer';
import { EditEnrollmentHeader } from './EditEnrollmentHeader';

interface EditEnrollmentProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
}

export const EditEnrollment = ({
  targetPopulation,
}: EditEnrollmentProps): React.ReactElement => {
  const { t } = useTranslation();
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
  const initialValues = {
    id: targetPopulation.id,
    name: targetPopulation.name || '',
    program: targetPopulation.program?.id || '',
    targetingCriteria: targetPopulation.targetingCriteria.rules || [],
    excludedIds: targetPopulation.excludedIds || '',
    exclusionReason: targetPopulation.exclusionReason || '',
  };
  const [mutate, { loading: loadingUpdateTP }] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();

  const { data, loading } = useCachedImportedIndividualFieldsQuery(
    businessArea,
  );
  useEffect(() => {
    if (loading) return;
    const filteredIndividualData = {
      allFieldsAttributes: data?.allFieldsAttributes
        ?.filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    };
    setIndividualData(filteredIndividualData);

    const filteredHouseholdData = {
      allFieldsAttributes: data?.allFieldsAttributes?.filter(
        associatedWith('Household'),
      ),
    };
    setHouseholdData(filteredHouseholdData);
  }, [data, loading]);
  if (!individualData || !householdData) return <LoadingComponent />;

  const handleValidate = (values): { targetingCriteria?: string } => {
    const { targetingCriteria } = values;
    const errors: { targetingCriteria?: string } = {};
    if (!targetingCriteria.length) {
      errors.targetingCriteria = t(
        'You need to select at least one targeting criteria',
      );
    }
    return errors;
  };
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(2, 'Too short')
      .max(255, 'Too long'),
    excludedIds: Yup.string().test(
      'testName',
      'ID is not in the correct format',
      (ids) => {
        if (!ids?.length) {
          return true;
        }
        const idsArr = ids.split(',');
        return idsArr.every((el) =>
          /^\s*(IND|HH)-\d{2}-\d{4}\.\d{4}\s*$/.test(el),
        );
      },
    ),
    exclusionReason: Yup.string().max(500, t('Too long')),
  });

  const handleSubmit = async (values, { setFieldError }): Promise<void> => {
    try {
      await mutate({
        variables: {
          input: {
            id: values.id,
            programId: values.program,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            ...(targetPopulation.status === TargetPopulationStatus.Open && {
              name: values.name,
            }),
            ...getTargetingCriteriaVariables({
              criterias: values.targetingCriteria,
            }),
          },
        },
      });
      showMessage(t('Target Population Updated'), {
        pathname: `/${businessArea}/target-population/${values.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      const { nonValidationErrors } = handleValidationErrors(
        'updateTargetPopulation',
        e,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(t('Unexpected problem while creating Target Population'));
      }
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validate={handleValidate}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ values, submitForm }) => {
        return (
          <Form>
            <EditEnrollmentHeader
              handleSubmit={submitForm}
              values={values}
              loading={loadingUpdateTP}
              businessArea={businessArea}
              targetPopulation={targetPopulation}
            />

            <FieldArray
              name='targetingCriteria'
              render={(arrayHelpers) => (
                <UniversalCriteriaPaperComponent
                  title='Enrollment Criteria'
                  isEdit
                  arrayHelpers={arrayHelpers}
                  rules={values.targetingCriteria}
                  householdFieldsChoices={householdData.allFieldsAttributes}
                  individualFieldsChoices={individualData.allFieldsAttributes}
                />
              )}
            />
            {/* //TODO: is it needed? */}
            <Exclusions />
            <PaperContainer>
              <Typography variant='h6'>
                {t('Save to see the list of enrollment entries.')}
              </Typography>
            </PaperContainer>
          </Form>
        );
      }}
    </Formik>
  );
};
