/* eslint-disable react-hooks/exhaustive-deps */
import React, { useCallback, useState } from 'react';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
  Snackbar,
  SnackbarContent,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@material-ui/core';
import ExitToAppRoundedIcon from '@material-ui/icons/ExitToAppRounded';
import {
  AllProgramsQuery,
  ProgramNode,
  ProgramStatus,
  useAllProgramsQuery,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { PROGRAM_QUERY } from '../../../apollo/queries/Program';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/AllPrograms';
import { programCompare } from '../../../utils/utils';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbarHelper } from '../../../hooks/useBreadcrumbHelper';
import { useDropzone } from 'react-dropzone';
import { Field, Form, Formik } from 'formik';
import { FormikSwitchField } from '../../../shared/Formik/FormikSwitchField';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;
const ComboBox = styled(Select)`
  & {
    min-width: 200px;
  }
`;
const DropzoneContainer = styled.div`
  width: 100%;
  height: 100px;
  background-color: rgba(2, 62, 144, 0.1);
  color: #023e90;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  line-height: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: ${({ theme }) => theme.spacing(5)}px;
`;

function DropzoneField({
  field,
  form,
  decoratorStart,
  decoratorEnd,
  type,
  precision,
  ...otherProps
}) {
  const onDrop = useCallback((acceptedFiles) => {
    console.log('test');
    field.onChange({
      target: { value: acceptedFiles[0], name: field.name },
    });
  }, []);
  const { getRootProps, getInputProps, acceptedFiles, rootRef } = useDropzone({
    onDrop,
  });
  const acceptedFilename =
    acceptedFiles.length > 0 ? acceptedFiles[0].name : null;
  return (
    <div>
      <DropzoneContainer {...getRootProps()}>
        <input {...getInputProps()} />
        {acceptedFilename || 'UPLOAD FILE'}
      </DropzoneContainer>
    </div>
  );
}

export function RegistrationDataImport(): React.ReactElement {
  const history = useHistory();
  const [open, setOpen] = useState(false);
  const snackBar = useSnackbarHelper();
  const businessArea = useBusinessArea();
  const { data } = useAllProgramsQuery({
    variables: { status: ProgramStatus.Draft },
  });
  const [importType, setImportType] = useState();
  const { t } = useTranslation();

  if (!data || !data.allPrograms) {
    return null;
  }
  const programChoices = data.allPrograms.edges.map((item) => ({
    name: item.node.name,
    value: item.node.id,
  }));
  return (
    <span>
      <Button
        variant='contained'
        color='primary'
        startIcon={<ExitToAppRoundedIcon />}
        onClick={() => setOpen(true)}
      >
        IMPORT
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <Formik
          onSubmit={(values) => {
            console.log({ values });
          }}
          initialValues={{}}
        >
          {({ submitForm, values }) => (
            <Form>
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title'>
                  <Typography variant='h6'>
                    {t('Select File to Import')}
                  </Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  Are you sure you want to activate this Programme and push data
                  to CashAssist?
                </DialogDescription>

                <FormControl
                  variant='filled'
                  margin='dense'
                >
                  <InputLabel>Import from</InputLabel>
                  <ComboBox
                    value={importType}
                    variant='filled'
                    label=''
                    onChange={(e) => setImportType(e.target.value)}
                    fullWidth
                  >
                    <MenuItem key='excel' value='excel'>
                      Excel
                    </MenuItem>
                    <MenuItem key='kobo' value='kobo'>
                      Kobo
                    </MenuItem>
                  </ComboBox>
                </FormControl>
                {importType === 'excel' ? (
                  <Field name='file' component={DropzoneField} />
                ) : null}
                <Field
                  name='name'
                  fullWidth
                  label='Name Upload'
                  component={FormikTextField}
                />

                <Field
                  name='program'
                  fullWidth
                  label='Program'
                  choices={programChoices}
                  component={FormikSelectField}
                />
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setOpen(false)}>CANCEL</Button>
                  <Button
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={() => {
                      submitForm();
                    }}
                  >
                    {t('IMPORT')}
                  </Button>
                </DialogActions>
              </DialogFooter>
            </Form>
          )}
        </Formik>
      </Dialog>
    </span>
  );
}
