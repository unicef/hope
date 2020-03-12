import React from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import { FormikTextField } from '../../shared/Formik/FormikTextField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const MediumLabel = styled.div`
  width: 60%;
  margin: 12px 0;
`;

const DateFields = styled.div`
  display: flex;
  justify-content: space-between;
  margin: 12px 0;
`;

const DateField = styled.div`
  width: 48%;
`;

const DialogContainer = styled.div`
  position: absolute;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Name is required'),
});

interface ProgramFormPropTypes {
  criteria?
  onSubmit: (values) => Promise<void>;
  renderSubmit: (submit: () => Promise<void>) => void;
  open: boolean;
  onClose: () => void;
  title: string;
}

export function TargetCriteriaForm({
  criteria,
  //onSubmit,
  //renderSubmit,
  open,
  onClose,
  title,
}): React.ReactElement {
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const initialValue: { [key: string]: any } = {
    name: '',
  
  };

  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={(values) => {
          const newValues = { ...values };
          newValues.budget = Number(values.budget).toFixed(2);
          return console.log(values);
        }}
        validationSchema={validationSchema}
      >
        {({ submitForm, values }) => (
          <Form>
            <Dialog
              open={open}
              onClose={onClose}
              scroll='paper'
              aria-labelledby='form-dialog-title'
            >
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>{title}</Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  Lorem ipsum dolor sit amet consectetur adipisicing elit. Natus tempora iusto maxime? Odit expedita ipsam natus eos? Inventore illo officiis laborum, quidem reprehenderit distinctio architecto aliquid obcaecati eius placeat dolorem.
                </DialogDescription>

                <Field
                  name='name'
                  label='Programme Name'
                  type='text'
                  fullWidth
                  required
                  component={FormikTextField}
                />
              </DialogContent>
              {/* {renderSubmit(submitForm)} */}
            </Dialog>
          </Form>
        )}
      </Formik>
    </DialogContainer>
  );
}
