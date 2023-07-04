import {
  Button,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import { FileCopy } from '@material-ui/icons';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { useCopyTargetPopulationMutation } from '../../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name is required'),
});

interface DuplicateProgramProps {
  programId: string;
}

export const DuplicateProgram = ({
  programId,
}: DuplicateProgramProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  //TODO: add useCopyProgramMutation
  const [mutate, { loading }] = useCopyTargetPopulationMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const initialValues = {
    name: '',
    id: programId,
  };

  return (
    <>
      <IconButton onClick={() => setOpen(true)}>
        <FileCopy />
      </IconButton>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <Formik
          validationSchema={validationSchema}
          initialValues={initialValues}
          onSubmit={async (values, { setFieldError }) => {
            //TODO: add try correct mutation input
            try {
              const res = await mutate({
                variables: { input: { targetPopulationData: { ...values } } },
              });
              setOpen(false);
              //TODO: add correct url
              showMessage(t('Programme Duplicated'), {
                pathname: `/${baseUrl}/details/${res.data.copyTargetPopulation.targetPopulation.id}`,
                historyMethod: 'push',
              });
            } catch (e) {
              e.graphQLErrors.map((x) => showMessage(x.message));
            }
          }}
        >
          {({ submitForm }) => (
            <>
              {open && <AutoSubmitFormOnEnter />}
              <DialogTitleWrapper>
                <DialogTitle>Duplicate Programme?</DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  {t(
                    'Please use a unique name for the copy of this Programme.',
                  )}
                  <br /> <strong>{t('Note')}</strong>:{' '}
                  {t(
                    'This duplicate will copy all the information from the original Programme.',
                  )}
                </DialogDescription>
                <Field
                  name='name'
                  fullWidth
                  label={t('Name Copy of Programme')}
                  required
                  variant='outlined'
                  component={FormikTextField}
                />
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button
                    data-cy='button-cancel'
                    onClick={() => setOpen(false)}
                  >
                    {t('CANCEL')}
                  </Button>
                  <LoadingButton
                    loading={loading}
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-programme-duplicate'
                  >
                    {t('Save')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </>
  );
};
