/* eslint-disable react-hooks/exhaustive-deps */
import { CircularProgress } from '@material-ui/core';
import { Field, FormikProvider, useFormik } from 'formik';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  ImportDataStatus, useAllActiveProgramsQuery,
  useCreateRegistrationXlsxImportMutation,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../../hooks/useSnackBar';
<<<<<<< HEAD
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
=======
import {FormikSelectField} from "../../../../shared/Formik/FormikSelectField";
import {LoadingComponent} from "../../../core/LoadingComponent";
import { useSaveXlsxImportDataAndCheckStatus } from './useSaveXlsxImportDataAndCheckStatus';
import { XlsxImportDataRepresentation } from './XlsxImportDataRepresentation';
>>>>>>> 6bba15b0bb56ca008d12ef456e490df910b96e3e
import { DropzoneField } from './DropzoneField';
import { XlsxImportDataRepresentation } from './XlsxImportDataRepresentation';
import { useSaveXlsxImportDataAndCheckStatus } from './useSaveXlsxImportDataAndCheckStatus';

const CircularProgressContainer = styled.div`
  display: flex;
  justify-content: center;
  align-content: center;
  width: 100%;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string()
    .required('Title is required')
    .min(2, 'Too short')
    .max(255, 'Too long'),
  programId: Yup.string()
    .required('Programme Name is required')
    .min(2, 'Too short')
    .max(150, 'Too long'),
});
export function CreateImportFromXlsxForm({
  setSubmitForm,
  setSubmitDisabled,
}): React.ReactElement {
  const {
    saveAndStartPolling,
    stopPollingImportData,
    loading: saveXlsxLoading,
    xlsxImportData,
  } = useSaveXlsxImportDataAndCheckStatus();
  const { baseUrl, businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const history = useHistory();
  const [createImport] = useCreateRegistrationXlsxImportMutation();

  const { data: programData, loading } = useAllActiveProgramsQuery({
    variables: {
      first: 100,
      businessArea: businessAreaSlug
    }
  });

  const onSubmit = async (values): Promise<void> => {
    try {
      const data = await createImport({
        variables: {
          registrationDataImportData: {
            importDataId: xlsxImportData.id,
            name: values.name,
            screenBeneficiary: values.screenBeneficiary,
<<<<<<< HEAD
            businessAreaSlug: businessArea,
=======
            businessAreaSlug,
            programId: values.programId
>>>>>>> 6bba15b0bb56ca008d12ef456e490df910b96e3e
          },
        },
      });
      history.push(
        `/${baseUrl}/registration-data-import/${data.data.registrationXlsxImport.registrationDataImport.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      screenBeneficiary: false,
      file: null,
      programId: ''
    },
    validationSchema,
    onSubmit,
  });
  // eslint-disable-next-line @typescript-eslint/require-await
  const saveXlsxInputData = async (): Promise<void> => {
    if (!formik.values.file) {
      return;
    }
    setSubmitDisabled(true);
    stopPollingImportData();
    await saveAndStartPolling({
      businessAreaSlug: businessArea,
      file: formik.values.file,
    });
  };
  useEffect(() => stopPollingImportData, []);
  useEffect(() => {
    saveXlsxInputData();
  }, [formik.values.file]);
  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);
  useEffect(() => {
    if (xlsxImportData?.status === ImportDataStatus.Finished) {
      setSubmitDisabled(false);
    }
  }, [xlsxImportData]);

  if (loading) {
    return <LoadingComponent />
  }

  const mappedProgramChoices = programData?.allActivePrograms?.edges?.map(
      (element) => ({name: element.node.name, value: element.node.id})
  );

  return (
    <div>
      <FormikProvider value={formik}>
        <DropzoneField loading={saveXlsxLoading} />
        <Field
          name='name'
          fullWidth
          label={t('Title')}
          required
          variant='outlined'
          component={FormikTextField}
        />
        <Field
          name='programId'
          label={t('Program Name')}
          fullWidth
          variant='outlined'
          required
          choices={mappedProgramChoices}
          component={FormikSelectField}
          data-cy='input-data-program-name'
        />
        <ScreenBeneficiaryField />
        <CircularProgressContainer>
          {saveXlsxLoading && <CircularProgress />}
        </CircularProgressContainer>
        <XlsxImportDataRepresentation
          xlsxImportData={xlsxImportData}
          loading={saveXlsxLoading}
        />
      </FormikProvider>
    </div>
  );
}
