/* eslint-disable react-hooks/exhaustive-deps */
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { Status753Enum } from '@restgenerated/models/Status753Enum';
import { useSnackbar } from '@hooks/useSnackBar';
import { useMutation } from '@tanstack/react-query';
import { Box, CircularProgress } from '@mui/material';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Field, FormikProvider, useFormik } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
import { DropzoneField } from './DropzoneField';
import { XlsxImportDataRepresentation } from './XlsxImportDataRepresentation';
import { useSaveXlsxImportDataAndCheckStatus } from './useSaveXlsxImportDataAndCheckStatus';

const CircularProgressContainer = styled.div`
  display: flex;
  justify-content: center;
  align-content: center;
  height: 50px;
  width: 100%;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string()
    .required('Title is required')
    .min(4, 'Too short')
    .max(255, 'Too long'),
});
export function CreateImportFromXlsxForm({
  setSubmitForm,
  setSubmitDisabled,
}): ReactElement {
  const {
    saveAndStartPolling,
    loading: saveXlsxLoading,
    xlsxImportData,
  } = useSaveXlsxImportDataAndCheckStatus();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const navigate = useNavigate();

  // Mutation for creating registration xlsx import
  const createImportMutation = useMutation({
    mutationFn: async (data: {
      importDataId: string;
      name: string;
      screenBeneficiary: boolean;
    }) => {
      return RestService.restBusinessAreasProgramsRegistrationDataImportsRegistrationXlsxImportCreate(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          requestBody: data,
        },
      );
    },
    onSuccess: (data) => {
      navigate(`/${baseUrl}/registration-data-import/${data.id}`);
    },
    onError: (error: any) => {
      showMessage(error.message || 'Error creating import');
      setSubmitDisabled(false);
    },
  });

  const onSubmit = (values): Promise<void> => {
    setSubmitDisabled(true);
    if (!xlsxImportData?.id) {
      setSubmitDisabled(false);
      return;
    }

    createImportMutation.mutate({
      importDataId: xlsxImportData.id,
      name: values.name,
      screenBeneficiary: values.screenBeneficiary,
    });
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      screenBeneficiary: false,
      file: null,
    },
    validationSchema,
    onSubmit,
  });
  const saveXlsxInputData = async (): Promise<void> => {
    if (!formik.values.file) {
      return;
    }
    setSubmitDisabled(true);
    await saveAndStartPolling({
      businessAreaSlug: businessArea,
      programSlug: programId,
      file: formik.values.file,
    });
  };
  useEffect(() => {
    saveXlsxInputData();
  }, [formik.values.file]);
  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);
  useEffect(() => {
    if (xlsxImportData?.status === Status753Enum.FINISHED) {
      setSubmitDisabled(false);
    } else {
      setSubmitDisabled(true);
    }
  }, [xlsxImportData]);

  return (
    <FormikProvider value={formik}>
      <DropzoneField loading={saveXlsxLoading} />
      <Box mt={2}>
        <Field
          name="name"
          fullWidth
          label={t('Title')}
          required
          variant="outlined"
          component={FormikTextField}
        />
      </Box>
      <ScreenBeneficiaryField />
      {saveXlsxLoading ? (
        <CircularProgressContainer>
          <CircularProgress />
        </CircularProgressContainer>
      ) : (
        <XlsxImportDataRepresentation
          xlsxImportData={xlsxImportData}
          loading={saveXlsxLoading}
        />
      )}
    </FormikProvider>
  );
}
