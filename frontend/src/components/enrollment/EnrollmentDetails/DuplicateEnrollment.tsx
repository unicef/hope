import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { LoadingButton } from '../../core/LoadingButton';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { handleValidationErrors } from '../../../utils/utils';
import { useCopyTargetPopulationMutation } from '../../../__generated__/graphql';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name is required'),
});

interface DuplicateEnrollmentProps {
  open: boolean;
  setOpen: Function;
  targetPopulationId: string;
}

export const DuplicateEnrollment = ({
  open,
  setOpen,
  targetPopulationId,
}: DuplicateEnrollmentProps): React.ReactElement => {
  const { t } = useTranslation();
  const [mutate, { loading }] = useCopyTargetPopulationMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const initialValues = {
    name: '',
    id: targetPopulationId,
  };

  return (
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
          try {
            const res = await mutate({
              variables: { input: { targetPopulationData: { ...values } } },
            });
            setOpen(false);
            showMessage(t('Enrollment Duplicated'), {
              pathname: `/${businessArea}/target-population/${res.data.copyTargetPopulation.targetPopulation.id}`,
              historyMethod: 'push',
            });
          } catch (e) {
            const { nonValidationErrors } = handleValidationErrors(
              'copyTargetPopulation',
              e,
              setFieldError,
              showMessage,
            );
            if (nonValidationErrors.length > 0) {
              showMessage(t('Unexpected problem while creating Enrollment.'));
            }
          }
        }}
      >
        {({ submitForm }) => (
          <>
            <DialogTitleWrapper>
              <DialogTitle>Duplicate Enrollment</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                {t('Please use a unique name for the copy of this Enrollment.')}
                <br /> <strong>{t('Note')}</strong>:{' '}
                {t(
                  'This duplicate will copy the Enrollment Criteria and update to the latest results from the system.',
                )}
              </DialogDescription>
              <Field
                name='name'
                fullWidth
                label={t('Name Copy of Enrollment')}
                required
                variant='outlined'
                component={FormikTextField}
              />
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                <LoadingButton
                  loading={loading}
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-target-population-duplicate'
                >
                  {t('Save')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        )}
      </Formik>
    </Dialog>
  );
};
