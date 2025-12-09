import React, { useEffect, useState } from 'react';
import { FieldArray, Form, Formik } from 'formik';
import styled from 'styled-components';
import { UniversalCriteriaPlainComponent } from './UniversalCriteriaPlainComponent';
import { UniversalCriteriaPaperComponent } from './UniversalCriteriaPaperComponent';
import { Paper } from '@mui/material';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { RestService } from '@restgenerated/index';
import { useQuery } from '@tanstack/react-query';

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

const associatedWith = (type) => (item) => item.associatedWith === type;
const isNot = (type) => (item) => item.type !== type;
export function Example(): React.ReactElement {
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
  const { businessArea, isAllPrograms } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const { data: allCoreFieldsAttributesData, isLoading: loading } = useQuery({
    queryKey: ['allFieldsAttributes', businessArea, selectedProgram?.id],
    queryFn: () =>
      RestService.restBusinessAreasAllFieldsAttributesList({
        slug: businessArea,
        programId: selectedProgram?.id,
      }),
    staleTime: 5 * 60 * 1000, // 5 minutes - equivalent to cache-first policy
    enabled: !!selectedProgram?.id && !isAllPrograms,
  });
  useEffect(() => {
    if (loading) return;
    const filteredIndividualData = {
      allFieldsAttributes: allCoreFieldsAttributesData?.results
        ?.filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    };
    setIndividualData(filteredIndividualData);

    const filteredHouseholdData = {
      allFieldsAttributes: allCoreFieldsAttributesData?.results?.filter(
        associatedWith('Household'),
      ),
    };
    setHouseholdData(filteredHouseholdData);
  }, [allCoreFieldsAttributesData, loading]);

  if (!individualData || !householdData) return <div>Loading</div>;

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
            {({ values, submitForm }) => {
              console.log('values', values);
              return (
                <Form style={{ width: '100%' }}>
                  <FieldArray
                    name="someWeirdNameForCriteria"
                    render={(arrayHelpers) => (
                      <UniversalCriteriaPlainComponent
                        isEdit
                        arrayHelpers={arrayHelpers}
                        rules={values.someWeirdNameForCriteria}
                        householdFieldsChoices={
                          householdData.allFieldsAttributes
                        }
                        individualFieldsChoices={
                          individualData.allFieldsAttributes
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
        {({ values, submitForm }) => {
          console.log('values', values);
          return (
            <Form style={{ width: '100%' }}>
              <FieldArray
                name="someWeirdNameForCriteria"
                render={(arrayHelpers) => (
                  <UniversalCriteriaPaperComponent
                    title="Example Paper Criteria"
                    isEdit
                    arrayHelpers={arrayHelpers}
                    rules={values.someWeirdNameForCriteria}
                    householdFieldsChoices={householdData.allFieldsAttributes}
                    individualFieldsChoices={individualData.allFieldsAttributes}
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
