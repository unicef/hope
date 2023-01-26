/* eslint-disable */
import { Paper } from '@material-ui/core';
import { FieldArray, Form, Formik } from 'formik';
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useCachedImportedIndividualFieldsQuery } from '../../../hooks/useCachedImportedIndividualFields';
import { associatedWith, isNot } from '../../../utils/utils';
import { UniversalCriteriaPaperComponent } from './UniversalCriteriaPaperComponent';
import { UniversalCriteriaPlainComponent } from './UniversalCriteriaPlainComponent';

export const ContentWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
  padding: ${({ theme }) => theme.spacing(4)}px
    ${({ theme }) => theme.spacing(4)}px;
`;

const PaperContainer = styled(Paper)`
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

export function Example(): React.ReactElement {
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
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
  const initialValues = {
    name: '',
    someWeirdNameForCriteria: [],
  };
  return (
    <div>
      <PaperContainer>
        <div>This can be for example other fields of program creation</div>
        <ContentWrapper>
          <Formik
            initialValues={initialValues}
            onSubmit={() => {
              console.log('XD');
            }}
          >
            {({ values }) => {
              console.log('values', values);
              return (
                <Form style={{ width: '100%' }}>
                  <FieldArray
                    name='someWeirdNameForCriteria'
                    render={(arrayHelpers) => (
                      <UniversalCriteriaPlainComponent
                        isEdit
                        arrayHelpers={arrayHelpers}
                        rules={values.someWeirdNameForCriteria}
                        householdFieldsChoices={
                          householdData?.allFieldsAttributes || []
                        }
                        individualFieldsChoices={
                          individualData?.allFieldsAttributes || []
                        }
                      />
                    )}
                  />
                </Form>
              );
            }}
          </Formik>
        </ContentWrapper>
      </PaperContainer>

      <Formik
        initialValues={initialValues}
        onSubmit={() => {
          console.log('XD');
        }}
      >
        {({ values }) => {
          console.log('values', values);
          return (
            <Form style={{ width: '100%' }}>
              <FieldArray
                name='someWeirdNameForCriteria'
                render={(arrayHelpers) => (
                  <UniversalCriteriaPaperComponent
                    title='Example Paper Criteria'
                    isEdit
                    arrayHelpers={arrayHelpers}
                    rules={values.someWeirdNameForCriteria}
                    householdFieldsChoices={
                      householdData?.allFieldsAttributes || []
                    }
                    individualFieldsChoices={
                      individualData?.allFieldsAttributes || []
                    }
                  />
                )}
              />
            </Form>
          );
        }}
      </Formik>
    </div>
  );
}
