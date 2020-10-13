import React from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import { FieldArray, Formik } from 'formik';
import { useImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { DialogActions } from '../dialogs/DialogActions';
import {
  chooseFieldType,
  clearField,
  formatCriteriaFilters,
  mapCriteriasToInitialValues,
} from '../../utils/targetingUtils';
import { TargetingCriteriaFilter } from './TargetCriteriaFilter';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const DialogContainer = styled.div`
  position: absolute;
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const StyledBox = styled(Box)`
  width: 100%;
`;

const validationSchema = Yup.object().shape({
  filters: Yup.array().of(
    Yup.object().shape({
      fieldName: Yup.string().required('Label is required'),
    }),
  ),
  individualsFiltersBlocks: Yup.array().of(
    Yup.array().of(
      Yup.object().shape({
        fieldName: Yup.string().required('Label is required'),
      }),
    ),
  ),
});

interface TargetCriteriaFormPropTypes {
  criteria?;
  addCriteria: (values) => void;
  open: boolean;
  onClose: () => void;
  title: string;
}

export function TargetCriteriaForm({
  criteria,
  addCriteria,
  open,
  onClose,
  title,
}: TargetCriteriaFormPropTypes): React.ReactElement {
  const { data, loading } = useImportedIndividualFieldsQuery();
  const mappedFilters = mapCriteriasToInitialValues(criteria);
  const initialValue = {
    filters: mappedFilters,
    individualsFiltersBlocks: [],
  };
  if (loading) return null;

  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={(values, bag) => {
          const dataToSend = formatCriteriaFilters(values);
          addCriteria({ filters: dataToSend });
          return bag.resetForm();
        }}
        validationSchema={validationSchema}
        enableReinitialize
      >
        {({ submitForm, values }) => (
          <>
            <FieldArray
              name='filters'
              render={(arrayHelpers) => (
                <>
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
                        Adding criteria below will target any individuals within
                        a household that meet the filters applied. You may also
                        add individual sub-criteria to further define an
                        individual.
                      </DialogDescription>
                      {values.filters.map((each, index) => {
                        return (
                          <TargetingCriteriaFilter
                            //eslint-disable-next-line
                            key={index}
                            index={index}
                            data={data}
                            each={each}
                            onChange={(e, object) => {
                              if (object) {
                                return chooseFieldType(
                                  object,
                                  arrayHelpers,
                                  index,
                                );
                              }
                              return clearField(arrayHelpers, index);
                            }}
                            values={values}
                            onClick={() => arrayHelpers.remove(index)}
                          />
                        );
                      })}
                      {/*{values.individualsFiltersBlocks.map((each, index) => {*/}

                      {/*})}*/}
                    </DialogContent>
                    <DialogFooter>
                      <DialogActions>
                        <StyledBox
                          display='flex'
                          justifyContent='space-between'
                        >
                          <div>
                            <Button
                              color='primary'
                              variant='outlined'
                              onClick={() =>
                                arrayHelpers.push({ fieldname: '' })
                              }
                            >
                              Add Next Criteria
                            </Button>
                          </div>
                          <div>
                            <Button onClick={() => onClose()}>Cancel</Button>
                            <Button
                              onClick={() => submitForm()}
                              type='submit'
                              color='primary'
                              variant='contained'
                              data-cy='button-target-population-add-criteria'
                            >
                              Save
                            </Button>
                          </div>
                        </StyledBox>
                      </DialogActions>
                    </DialogFooter>
                  </Dialog>
                </>
              )}
            />
          </>
        )}
      </Formik>
    </DialogContainer>
  );
}
